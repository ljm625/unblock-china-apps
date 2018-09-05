import time
import yaml
import re
import requests


class BlocksitesUpdater(object):

    regex_rules=r'http.?://\*?([0-9A-Za-z.\-]*)/'
    def __init__(self,url):
        self.url=url.format(time=int(time.time()*100))
        self.get()
        self.parse_domain_list()

    def get(self):
        resp = requests.get(self.url)
        self.data = [i.strip('"') for i in resp.text.split(',')]
        return self.data



    def parse_domain_list(self):
        domain = set()
        for data in self.data:
            result=re.search(self.regex_rules, data)
            try:
                domain.add(result.group(1).strip("."))
            except:
                pass
        self.domain=domain






