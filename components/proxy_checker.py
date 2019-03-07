import logging
import requests
import yaml


class ProxyChecker(object):
    best_proxy=None
    instance=None
    def __init__(self,proxy_list,check_url,speedtest_url,timeout=10,checker_timeout=20,speedtest_times=1,black_list=[],enable_socks=True,enable_http=True):
        self.proxy_list=proxy_list
        self.check_url=check_url
        self.timeout=timeout
        self.checker_timeout=checker_timeout
        self.speedtest_url=speedtest_url
        self.speedtest_times = speedtest_times
        self.black_list=black_list
        self.enable_http=enable_http
        self.enable_socks=enable_socks

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
            https_enabled = config.get('https_enabled')
            if https_enabled:
                speedtest_url=config.get('speedtest_url_https')
            else:
                speedtest_url=config.get('speedtest_url')
            timeout=config.get('timeout')
            checker_timeout=config.get('checker_timeout')
            speedtest_times=config.get("speedtest_times")
            black_list=config.get("proxy_domain")
            enable_socks=config.get("enable_socks")
            enable_http=config.get("enable_http")

            if check_url and timeout:
                cls.instance=cls(proxy_list=proxy_list,check_url=check_url,speedtest_url=speedtest_url,timeout=timeout,
                                 checker_timeout=checker_timeout,speedtest_times=speedtest_times,black_list=black_list,enable_socks=enable_socks,enable_http=enable_http)
                return cls.instance
            else:
                raise Exception("ERROR : The Config URL is missing")

    def validate_proxy(self,proxy,check=False):
        def build_proxy():
            if proxy[2]=='HTTP' or proxy[2]=="HTTPS":
                return {"http": "http://{}:{}".format(proxy[0],proxy[1]),
                        "https": "http://{}:{}".format(proxy[0],proxy[1])}
            elif proxy[2]=='SOCKS5':
                return {"http": "socks5://{}:{}".format(proxy[0],proxy[1]),
                        "https": "socks5://{}:{}".format(proxy[0],proxy[1])}
        try:
            if (proxy[2]=='HTTP' or proxy[2]=="HTTPS") and self.enable_http:
                pass
            elif proxy[2]=='SOCKS5' and self.enable_socks:
                pass
            else:
                return None

            if check:
                resp = requests.get(self.check_url, proxies=build_proxy(), timeout=self.checker_timeout)
            else:
                resp=requests.get(self.check_url,proxies=build_proxy(),timeout=self.timeout)
            if resp.status_code < 300 and resp.json()['countryCode']=='CN':
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
        logging.info("Best Proxy: {}:{} {}".format(self.best_proxy[0], self.best_proxy[1], self.best_proxy[2]))


    def get_proxy(self,refresh=False):
        if self.best_proxy and not refresh:
            return self.best_proxy
        else:
            self.get_best_proxy()
            return self.best_proxy

    def update_list(self,list):
        self.proxy_list=list