import socket
import SocketServer
import threading
from time import sleep

import logging
import yaml

from components.proxy_checker import ProxyChecker


class Forwarder(threading.Thread):
    alive = True
    def __init__(self, source, dest, buffer_size):
        threading.Thread.__init__(self)
        self.source = source
        self.dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dest.connect((dest[0], int(dest[1])))
        if buffer_size:
            self.buffer_size = buffer_size
        else:
            self.buffer_size = 4096
        logging.info("Connect to Forwarder:{}:{}".format(dest[0], dest[1]))

    def run(self):
        # logging.info("starting forwarder... ")

        try:
            while True:
                data = self.dest.recv(self.buffer_size)
                if len(data) == 0:
                    raise Exception("endpoint closed")
                # logging.info("Received from dest: " + str(len(data)))
                self.source.write_to_source(data)
        except Exception as e:
            self.alive = False
            logging.warning("Exception reading from forwarding socket : {}".format(e))

        self.source.stop_forwarding()
        # logging.info("...ending forwarder.")

    def write_to_dest(self, data):
        # logging.info("Sending to dest: " + str(len(data)))
        self.dest.send(data)

    def stop_forwarding(self):
        # logging.info("...closing forwarding socket")
        self.alive = False
        self.dest.close()

    def check_alive(self):
        return self.alive

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.proxy = ProxyChecker.get_instance()
        self.config = self.get_config()
        self.black_list = self.config['proxy_domain']
        while not self.proxy:
            sleep(5)
            logging.info("INFO : Waiting for proxy list to be generated...")
            self.proxy = ProxyChecker.get_instance()
        SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)

    def get_config(self):
        json = {}
        with open('config.yaml') as file:
            json = yaml.load(file)
        return json

    def get_orig_host(self,input):
        datas = str(input).split('\r\n')
        for data in datas:
            if 'Host:' in data:
                data_list=data.split(":")
                if len(data_list)==2:
                    return data_list[1].strip(), 80
                elif len(data_list)==3:
                    return data_list[1].strip(), int(data_list[2].strip())
        return None,None

    def handle(self):
        # logging.info("Starting to handle connection...")

        f = Forwarder(self, self.proxy.get_proxy(), self.config.get('buffer_size'))
        f.start()
        first_time = True
        logging.info("Received a connection from: {}:{}".format(self.client_address[0], self.client_address[1]))
        try:
            while True:
                if f.check_alive():
                    data = self.request.recv(4096)
                    if len(data) == 0:
                        raise Exception("endpoint closed")
                    if first_time:
                        if "Host" in data:
                            host, port = self.get_orig_host(data)
                            if host and port:
                                # Change forwarder
                                use_proxy = False
                                for domain in self.black_list:
                                    if domain in host:
                                        use_proxy = True
                                if not use_proxy:
                                    logging.info("Using DIRECT Connection for the request : {}:{}".format(host, port))
                                    f.stop_forwarding()
                                    f = Forwarder(self, [host, port], self.config.get('buffer_size'))
                                    f.start()
                        first_time = False
                    # logging.info("Received from source: " + str(len(data)))
                    f.write_to_dest(data)
                else:
                    raise Exception("Forwarder is dead.")
        except Exception as e:
            logging.warning("Exception reading from forwarding socket : {}".format(e))

        f.stop_forwarding()
        logging.info("Connection Closed :{}:{}".format(self.client_address[0], self.client_address[1]))

    def write_to_source(self, data):
        # logging.info("Sending to source: " + str(len(data)))
        self.request.send(data)

    def stop_forwarding(self):
        # logging.info("...closing main socket")
        self.request.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address=("", self.get_config()['proxy_port']),
                                        RequestHandlerClass=RequestHandlerClass)

    def get_config(self):
        json = {}
        with open('config.yaml') as file:
            json = yaml.load(file)
        return json
