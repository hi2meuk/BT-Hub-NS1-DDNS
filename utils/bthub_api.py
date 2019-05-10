import requests
import urllib.parse
from xml.etree import ElementTree as ET
import re
from collections import namedtuple
import logging

sq_brackets = re.compile(r'\[(.+)\]')
squotes = re.compile(r"\'(.+)\'")

# data structures
WanConnData = namedtuple('WanConnData', 'desc code xxx')
WanVolumeData = namedtuple('WanVolumeData', 'total rx tx')
WanIP4 = namedtuple('WanIP4', 'addr mask gateway dns1 dns2')
ConnRate = namedtuple('ConnRate', 'up_bps down_bps up_x down_x')
Hub5Status = namedtuple('Hub5Status', 'wan_conn_data wan_volume_data wan_ip4 conn_rate')


log = logging.getLogger(__name__)


# helper functions
def value_from(be, name):
    '''Searches for sub element name and returns the value of the
    attribute @value, or empty string if not found
    '''
    te = be.find(name)
    return te.attrib.get('value', '')


# def print_xmldoc(doc):
#     'Prints an xml doc. Used for debugging'
#     print(ET.tostring(doc, pretty_print=True, encoding='utf-8').decode())
#     print(ET.tostring(doc, pretty_print=True, encoding='utf-8').decode())


def strip_outer(rexp, s: str):
    'Returns the string within encapsulating chars defined by the given regexp'
    m = re.match(rexp, s)
    return m.group(1) if m else s


# API class for BT Hub 5
class Hub5_API():

    def __init__(self, hub_ip: str ='192.168.1.254'):
        self.hub_ip = hub_ip

    @staticmethod
    def extract_record(s: str, idx: int):
        'Given a text record array, extract the record according to given index and format it to something more useful'
        s = strip_outer(sq_brackets, s)
        s = strip_outer(sq_brackets, s.split(', ')[idx])
        s = urllib.parse.unquote(strip_outer(squotes, s))
        return s.split(';')

    def get_status(self):
        try:
            wan_status_url = f'http://{self.hub_ip}/nonAuth/wan_conn.xml'
            response = requests.get(wan_status_url)
            response.raise_for_status()
        except requests.HTTPError as e:
            logging.error(e)
            return

        doc = ET. fromstring(response.content)

        idx = value_from(doc, 'wan_active_idx')
        if not idx:
            logging.warn(doc)
            return
        idx = int(idx)

        link_status = Hub5_API.extract_record(value_from(doc, 'curlinkstatus'), idx)[0]
        if link_status == 'connected':

            a = Hub5_API.extract_record(value_from(doc, 'wan_conn_status_list'), idx)
            wan_conn = WanConnData(*a)

            a = Hub5_API.extract_record(value_from(doc, 'wan_conn_volume_list'), idx)
            wan_volumes = WanVolumeData(*a)

            a = Hub5_API.extract_record(value_from(doc, 'ip4_info_list'), idx)
            wan_ip = WanIP4(*a)

            a = Hub5_API.extract_record(value_from(doc, 'status_rate'), idx)
            conn_rate = ConnRate(*[int(v or 0) for v in a])

            return Hub5Status(wan_conn, wan_volumes, wan_ip, conn_rate)

        else:
            logging.warn(response.text)
