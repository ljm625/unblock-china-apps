# This file is used to pick correct proxy and save to localhost.
from time import sleep
import threading

import logging
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
            list = self.fetcher.get_proxy_list(refresh=True)
            self.checker.update_list(list)
            proxy=self.checker.get_proxy(refresh=True)
        except AttributeError as e:
            list = self.fetcher.get_proxy_list(refresh=True)
            self.checker.update_list(list)
            proxy = self.checker.get_proxy(refresh=True)

    def run(self):
        logging.info("Started the Helper thread.")
        secs = 0
        logging.info("Start the pre-run session.")
        self.get_new_proxy()
        while not self.stop_job:
            if secs >= self.config.get('check_interval'):
                secs = 0
                if not self.checker.validate_proxy(self.checker.get_proxy(),check=True):
                    logging.info("Getting new proxy.")
                    self.get_new_proxy()
            elif self.stop_job:
                logging.info("Stopping the helper thread.")
                break
            else:
                sleep(3)
                secs += 3

    def stop(self):
        self.stop_job=True