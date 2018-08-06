

"""
This class is only used to store the Value for Async Loop
"""

import yaml
from multiprocessing import Manager


class ProxyHelper(object):
    instance = None
    def __init__(self,black_list=[]):
        manager = Manager()
        self._proxy = manager.list()
        self.black_list=black_list

    @classmethod
    def get_instance(cls):
        def yaml_loader(file):
            with open(file) as f:
                return yaml.load(f)

        if cls.instance:
            return cls.instance
        else:
            config = yaml_loader('config.yaml')
            black_list = config.get("proxy_domain")
            cls.instance=cls(black_list)

            return cls.instance

    def get_proxy(self):
        # print("GETTING PROXY!")
        return list(self._proxy)

    def set_proxy(self,value):
        # print("SETTING PROXY!")
        if not value:
            return
        else:
            self._proxy[0]=value[0]
            self._proxy[1]=value[1]

    def set_proxy_addr(self,host,port):
        if len(self._proxy)==0:
            self._proxy.append(host)
            self._proxy.append(port)
        else:
            self._proxy[0]=host
            self._proxy[1]=port

    proxy = property(get_proxy,set_proxy)
