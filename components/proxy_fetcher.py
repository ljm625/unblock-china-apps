import logging
import requests
import yaml
from bs4 import BeautifulSoup

class ProxyFetcher(object):
    instance = None
    proxys=None
    def __init__(self,url,candidate_num=5):
        self.url=url
        self.candidate=candidate_num

    @classmethod
    def get_instance(cls):
        def yaml_loader(file):
            with open(file) as f:
                return yaml.load(f)

        if cls.instance:
            return cls.instance
        else:
            config=yaml_loader('config.yaml')
            url=config.get('proxy_url')
            candidate=config.get('candidate_num')
            if url and candidate:
                cls.instance=cls(url,candidate_num=candidate)
                return cls.instance
            else:
                raise Exception("ERROR : The Config URL is missing")

    def proxy_fetcher(self):
        resp=requests.get(self.url)
        if resp.status_code<300:
            return resp.content
        else:
            raise Exception("ERROR : The Proxy Website is DOWN.")

    def proxy_parser(self):
        data=self.proxy_fetcher()
        soup = BeautifulSoup(data,"html5lib")
        proxy_list=soup.select("tbody tr")
        self.proxys=[]
        for i in range(0,self.candidate):
            try:
                self.proxys.append([proxy_list[i].select("td:nth-of-type(1)")[0].text.strip(),proxy_list[i].select("td:nth-of-type(2)")[0].text.strip()])
            except Exception as e:
                logging.error("{}".format(e))

    def get_proxy_list(self,refresh=False):
        if self.proxys and not refresh:
            return self.proxys
        else:
            self.proxy_parser()
            return self.proxys
