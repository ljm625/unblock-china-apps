# This file is used to pick correct proxy and save to localhost.
from time import sleep
import threading
import yaml

from components.proxy_checker import ProxyChecker
from components.proxy_fetcher import ProxyFetcher


class Helper(threading.Thread):
    stop_job = False

    def __init__(self,threadID,name,config_file='config.yaml'):
        threading.Thread.__init__(self,name=name)
        self.threadID = threadID
        self.name = name
        self.config=self.yaml_reader(config_file)
        self.fetcher = ProxyFetcher.get_instance()
        list = self.fetcher.get_proxy_list()
        self.checker = ProxyChecker.get_instance(list)


    def yaml_reader(self,config):
        with open(config) as f:
            return yaml.load(f)

    def get_new_proxy(self):
        try:
            proxy=self.checker.get_proxy(refresh=True)
        except AttributeError as e:
            list = self.fetcher.get_proxy_list(refresh=True)
            self.checker.update_list(list)
            proxy = self.checker.get_proxy(refresh=True)

    def run(self):
        print("INFO : Started the Helper thread.")
        secs = 0
        print("INFO : Start the pre-run session.")
        self.get_new_proxy()
        while not self.stop_job:
            if secs == self.config.get('check_interval'):
                secs = 0
                if not self.checker.validate_proxy(self.checker.get_proxy()):
                    print("INFO : Getting new proxy.")
                    self.get_new_proxy()
            else:
                sleep(1)
                secs += 1

    def stop(self):
        self.stop_job=True