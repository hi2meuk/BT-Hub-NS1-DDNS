from ns1 import NS1
import logging
# based on zone example, see examples in https://pypi.org/project/api-python/

logger = logging.getLogger(__name__)


class NS1_API():

    def __init__(self, apikey, domain):
        # not bothering with zone
        self.api = NS1(apikey)
        self.domain = domain
        self.ip_cache = None
        self.rec = self.api.loadRecord(self.domain, 'A')

    def update(self, new_ip_address):
        answers = self.rec.data['answers']
        ip_cache = answers[0]['answer'][0] if answers else ''
        if new_ip_address != ip_cache:
            logger.info(f'Updating DNS with {new_ip_address} was {self.ip_cache}')
            self.rec.update(answers=[new_ip_address])
