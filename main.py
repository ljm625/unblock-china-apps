#!/usr/bin/python
import asyncio
import sys
import threading
from time import sleep

import os

from multiprocessing import Value

import yaml

from async_proxy import handle_client
from components.blocksites_updater import BlocksitesUpdater
from components.pac_generator import PacGenerator
from components.proxy_checker import ProxyChecker
from components.proxy_helper import ProxyHelper
from helper import Helper
from helper_dns import HelperDns
import logging


def yaml_loader(file):
    with open(file) as f:
        return yaml.load(f)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    config = yaml_loader("config.yaml")
    if config.get('enable_blocksites_updater'):
        block_generator = BlocksitesUpdater(config.get("updater_url"))
    else:
        block_generator = None

    PacGenerator("config.yaml",block_generator.data if block_generator else None).build_pac()



    # pid = os.fork()
    # if pid == 0:
    #     print(('I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid())))
    #
    #     try:
    #         while True:
    #             sleep(1)
    #     except KeyboardInterrupt:
    #         logging.info("User shutdown request received. Starting to shutdown")
    #     except Exception as e:
    #         logging.error("Critical Unknown issue received. Shutting down. {}".format(e))
    #     logging.info("All Shutdown")
    #     sys.exit(1)
    # else:
    #     print(('I (%s) just created a child process (%s).' % (os.getpid(), pid)))
        # Global Proxy across processes.

    # Start DNS Server.
    if config["dns_enabled"]:
        pid = os.fork()
        if pid == 0:
            helper_dns = HelperDns("config.yaml")
            print("INFO : DNS Server Enabled")
            helper_dns.start()
            try:
                while True:
                    sleep(1)
            except KeyboardInterrupt:
                logging.info("User shutdown request received. Starting to shutdown")
            except Exception as e:
                logging.error("Critical Unknown issue received. Shutting down. {}".format(e))
            logging.info("All Shutdown")
            helper_dns.stop()
            sys.exit(1)

    proxy_helper=ProxyHelper.get_instance()

    if block_generator:
        proxy_helper.black_list=list(block_generator.domain)

    helper = Helper("Helper",proxy_helper)
    helper.start()

    # server = ForkedTCPServer(ThreadedTCPRequestHandler)
    # ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    # server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    logging.info("Sleep a little bit for the proxy to complete..")
    sleep(10)
    # test_proxy = ProxyChecker.get_instance()
    # while not proxy.value:
    #     sleep(5)
    #     logging.info("INFO : Waiting for proxy list to be generated...")
        # test_proxy = ProxyChecker.get_instance()
    while len(proxy_helper.proxy)==0:
        sleep(5)
        logging.info("INFO : Waiting for best proxy to be find...")

    print('Serving on {}:{}'.format(config["proxy_address"],config["proxy_port"]))

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_client, config["proxy_address"], config["proxy_port"], loop=loop)
    server = loop.run_until_complete(coro)


    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("User shutdown request received. Starting to shutdown")
    except Exception as e:
        logging.error("Critical Unknown issue received. Shutting down. {}".format(e))

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    helper.stop()
    logging.info("Helper Stopped")
    # server.shutdown()
    logging.info("All Shutdown")
    sys.exit(1)
