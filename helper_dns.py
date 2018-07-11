# This file is used to start a custom dns server for proxy.
from multiprocessing import Process
from time import sleep
import threading

import logging

import os
import requests
import yaml

from components.dns_server import Resolver
from dnslib.server import DNSServer


class HelperDns(Process):
    stop_job = False

    def __init__(self,config_file='config.yaml'):
        self.config=self.yaml_reader(config_file)
        self.upstream = self.config['upstream_dns']
        self.port = self.config['dns_port']
        self.dns_data=[]
        self.generate_dns_config()

    def yaml_reader(self,config):
        with open(config) as f:
            return yaml.load(f)

    def get_ip(self):
        try:
            resp = requests.get("https://api.ipify.org?format=json", timeout=2)
            if resp.status_code>300:
                return "127.0.0.1"
            else:
                return resp.json()['ip'].strip()
        except:
            return "127.0.0.1"

    def generate_dns_config(self):
        ip_addr=""
        try:
            ip_addr=os.environ["IPADDR"]
        except:
            ip_addr=self.get_ip()

        for url in self.config['proxy_domain']:
            self.dns_data.append({"rname":url,"rtype":"A","args":ip_addr})




    def start(self):

        resolver = Resolver(self.upstream, self.dns_data)
        self.udp_server = DNSServer(resolver, port=self.port)
        self.tcp_server = DNSServer(resolver, port=self.port, tcp=True)
        self.udp_server.start_thread()
        self.tcp_server.start_thread()

    def stop(self):
        self.stop_job=True