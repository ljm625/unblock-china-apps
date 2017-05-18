#!/usr/bin/python
import sys

from components.pac_generator import PacGenerator
from helper import Helper
from proxy import TheServer

if __name__ == '__main__':
        PacGenerator("config.yaml").build_pac()
        helper=Helper(1,"Thread-1")
        helper.start()
        server = TheServer('')
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            helper.stop()
            sys.exit(1)