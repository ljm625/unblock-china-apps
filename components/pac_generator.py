import requests
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader
import os

from components.blocksites_updater import BlocksitesUpdater


class PacGenerator(object):
    def __init__(self,config,block_list=None):
        self.env = Environment(loader=FileSystemLoader('template'))
        def yaml_loader(file):
            with open(file) as f:
                return yaml.load(f)
        self.config=yaml_loader(config)
        self.block_list=block_list


    def get_ip(self):
        try:
            resp = requests.get("https://api.ipify.org?format=json", timeout=2)
            if resp.status_code>300:
                return "127.0.0.1"
            else:
                return resp.json()['ip'].strip()
        except:
            return "127.0.0.1"

    def build_pac(self):
        info={}
        if self.block_list:
            info['block_urls']=self.block_list
        else:
            info['block_urls']=self.config['dns_domain']
        info['direct_urls']=self.config['direct_urls']
        try:
            info['proxy_ip']=os.environ["IPADDR"]
        except:
            info['proxy_ip']=self.get_ip()
        info['proxy_port']=self.config.get("proxy_port")
        template = self.env.get_template("new_proxy.pac")
        self.file_writer(template.render(info=info))

    def file_writer(self,data):
        with open("pac/proxy.pac",'w+') as file:
            file.write(data)

