from utils.ns1_api import NS1_API
from utils.bthub_api import Hub5_API
from time import sleep
import json
import logging


SETTINGS_FILENAME = 'settings.json'


# Load JSON config file
with open(SETTINGS_FILENAME) as f:
    doc = f.read()
    conf = json.loads(doc)

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=conf['LOG_LEVEL']
)
logger = logging.getLogger(__name__)

hub = Hub5_API()
dns = NS1_API(conf['NS1_APIKEY'], conf['NS1_DOMAIN'])


last_ip = ''
while True:
    hub_status = hub.get_status()
    if hub_status is None:
        logger.warn('could not get status from BT router')
    else:
        logger.debug(f'connection status: {hub_status.wan_conn_data.desc}')
        if hub_status.wan_conn_data.desc != 'connected':
            sleep(conf['DISCONNECTED_INTERVAL'])
            continue
        if last_ip != hub_status.wan_ip4.addr and hub_status.wan_ip4.addr != '0.0.0.0':
            if last_ip:
                logger.info('WAN IP address changed from {last_ip} to {hub_status.wan_ip4.addr}')
            else:
                logger.info(f'WAN IP address is {hub_status.wan_ip4.addr}')

            down = hub_status.conn_rate.down_bps / 1e6
            up = hub_status.conn_rate.up_bps / 1e6
            logger.info(f'connection bit rate (down/up) {down:1.2f}/{up:1.2f}')

            dns.update(hub_status.wan_ip4.addr)
            last_ip = hub_status.wan_ip4.addr
    sleep(conf['CONNECTED_INTERVAL'])
