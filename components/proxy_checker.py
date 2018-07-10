import logging
import requests
import yaml


class ProxyChecker(object):
    best_proxy=None
    instance=None
    def __init__(self,proxy_list,check_url,speedtest_url,timeout=10,checker_timeout=20,speedtest_times=1):
        self.proxy_list=proxy_list
        self.check_url=check_url
        self.timeout=timeout
        self.checker_timeout=checker_timeout
        self.speedtest_url=speedtest_url
        self.speedtest_times = speedtest_times

    @classmethod
    def get_instance(cls,proxy_list=None):
        def yaml_loader(file):
            with open(file) as f:
                return yaml.load(f)

        if cls.instance:
            return cls.instance
        elif not proxy_list:
            return None
        else:
            config=yaml_loader('config.yaml')
            check_url=config.get('validate_url')
            speedtest_url=config.get('speedtest_url')
            timeout=config.get('timeout')
            checker_timeout=config.get('checker_timeout')
            speedtest_times=config.get("speedtest_times")
            if check_url and timeout:
                cls.instance=cls(proxy_list=proxy_list,check_url=check_url,speedtest_url=speedtest_url,timeout=timeout,checker_timeout=checker_timeout,speedtest_times=speedtest_times)
                return cls.instance
            else:
                raise Exception("ERROR : The Config URL is missing")

    def validate_proxy(self,proxy,check=False):
        def build_proxy():
            return {"http": "http://{}:{}".format(proxy[0],proxy[1]) }
        try:
            if check:
                resp = requests.get(self.check_url, proxies=build_proxy(), timeout=self.checker_timeout)
            else:
                resp=requests.get(self.check_url,proxies=build_proxy(),timeout=self.timeout)
            if resp.status_code < 300 and resp.text=='true':
                total_time =0
                for i in range(0,self.speedtest_times):
                    resp_speed = requests.get(self.speedtest_url,proxies=build_proxy(),timeout=self.timeout)
                    if resp_speed.status_code> 300:
                        raise Exception("Error:Server Speed too slow.")
                    # TODO : The netease validate link always return false whether it's mainland or not
                    total_time += resp_speed.elapsed.total_seconds()*1000
                return total_time
            return None
        except Exception as e:
            return None

    def get_best_proxy(self):
        best=None
        min_latency=None
        for proxy in self.proxy_list:
            result = self.validate_proxy(proxy)
            if result:
                if not best:
                    best=proxy
                    min_latency=result
                else:
                    if result<min_latency:
                        best=proxy
                        min_latency=result
        if not best:
            raise AttributeError("ERROR : No available servers! ")
        self.best_proxy=best
        logging.info("Best Proxy: {}:{}".format(self.best_proxy[0], self.best_proxy[1]))


    def get_proxy(self,refresh=False):
        if self.best_proxy and not refresh:
            return self.best_proxy
        else:
            self.get_best_proxy()
            return self.best_proxy

    def update_list(self,list):
        self.proxy_list=list