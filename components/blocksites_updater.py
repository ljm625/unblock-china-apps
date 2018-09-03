import time

import re
import requests


class BlocksitesUpdater(object):

    regex_rules=r'http.?://([0-9A-Za-z.]*)/'
    def __init__(self,url):
        self.url=url
        pass

    def get(self):
        resp = requests.get(self.url)
        self.data = [i.strip('"') for i in resp.text.split(',')]



    def parse_domain_list(self):
        domain = set()
        for data in self.data:
            result=re.search(self.regex_rules, data)
            domain.add(result.group(1))
        return domain





