#!/usr/bin/python
import sys
import threading
from time import sleep

from components.pac_generator import PacGenerator
from components.proxy_checker import ProxyChecker
from helper import Helper
from proxy import ForkedTCPServer, ThreadedTCPRequestHandler
from proxy_deprecated import TheServer
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    PacGenerator("config.yaml").build_pac()
    helper = Helper(1, "Thread-1")
    helper.start()

    server = ForkedTCPServer(ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    logging.info("Sleep a little bit for the proxy to complete..")
    sleep(10)
    test_proxy = ProxyChecker.get_instance()
    while not test_proxy:
        sleep(5)
        logging.info("INFO : Waiting for proxy list to be generated...")
        test_proxy = ProxyChecker.get_instance()
    while not test_proxy.best_proxy:
        sleep(5)
        logging.info("INFO : Waiting for best proxy to be find...")

    server_thread.start()
    logging.info("Server Running at {}".format(port))
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logging.info("User shutdown request received. Starting to shutdown")
    except Exception as e:
        logging.error("Critical Unknown issue received. Shutting down. {}".format(e))
    helper.stop()
    logging.info("Helper Stopped")
    server.shutdown()
    logging.info("All Shutdown")
    sys.exit(1)
