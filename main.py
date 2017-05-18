#!/usr/bin/python
import sys
import threading
from time import sleep

from components.pac_generator import PacGenerator
from helper import Helper
from proxy import ThreadedTCPServer, ThreadedTCPRequestHandler
from proxy_deprecated import TheServer

if __name__ == '__main__':
        PacGenerator("config.yaml").build_pac()
        helper=Helper(1,"Thread-1")
        helper.start()

        server = ThreadedTCPServer(ThreadedTCPRequestHandler)
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        print("Sleep a little bit for the proxy to complete..")
        sleep(10)
        server_thread.start()
        print("Server loop running on port ", port)
        try:
            while True:
                sleep(1)
        except:
            pass
        print("...server stopping.")
        helper.stop()
        server.shutdown()
