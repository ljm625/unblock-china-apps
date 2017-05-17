from components.pac_generator import PacGenerator
from components.proxy_checker import ProxyChecker
from components.proxy_fetcher import ProxyFetcher

print("Test Debug")
# # fet=ProxyFetcher("http://cn-proxy.com")
# fetcher=ProxyFetcher.get_instance()
# list=fetcher.get_proxy_list()
# checker=ProxyChecker(list,"http://ipservice.163.com/isFromMainland")
# print(checker.get_proxy())

pac=PacGenerator('config.yaml')
pac.build_pac()