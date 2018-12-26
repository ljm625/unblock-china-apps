import logging
import requests
import yaml
from bs4 import BeautifulSoup
from profile.proxy_rules import get_data_on_profile

class ProxyFetcher(object):
    instance = None
    proxys=None
    def __init__(self,urls,candidate_num=5):
        self.urls=urls
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
            urls=config.get('proxy_urls')
            candidate=config.get('candidate_num')
            if urls and candidate:
                cls.instance=cls(urls,candidate_num=candidate)
                return cls.instance
            else:
                raise Exception("ERROR : The Config URL is missing")

    def proxy_fetcher(self,url):
        resp=requests.get(url)
        if resp.status_code<300:
            return resp.content
        else:
            raise Exception("ERROR : The Proxy Website is DOWN.")

    def proxy_parser(self):
        try:
            self.proxys=[]
            for server in self.urls:
                data=self.proxy_fetcher(server['url'])
                soup = BeautifulSoup(data,"html5lib")
                try:
                    self.proxys.extend(get_data_on_profile(server['name'],soup,self.candidate))
                except Exception as e:
                    pass
            print("Got Proxies:")
            print((self.proxys))
        except Exception as e:
            logging.error("{}".format(e))

    def get_proxy_list(self,refresh=False):
        if self.proxys and not refresh:
            return self.proxys
        else:
            self.proxy_parser()
            return self.proxys
