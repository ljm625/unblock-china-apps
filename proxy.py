import socket
import SocketServer
import threading
from time import sleep

import yaml

from components.proxy_checker import ProxyChecker


class Forwarder(threading.Thread):
    def __init__(self, source, dest):
        threading.Thread.__init__(self)
        self.source = source
        self.dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dest.connect((dest[0], int(dest[1])))
        print("Connect to Forwarder:{}:{}".format(dest[0], dest[1]))

    def run(self):
        # print("starting forwarder... ")

        try:
            while True:
                data = self.dest.recv(4096)
                if len(data) == 0:
                    raise Exception("endpoint closed")
                # print("Received from dest: " + str(len(data)))
                self.source.write_to_source(data)
        except Exception as e:
            print("EXCEPTION reading from forwarding socket")
            print(e)

        self.source.stop_forwarding()
        # print("...ending forwarder.")

    def write_to_dest(self, data):
        # print("Sending to dest: " + str(len(data)))
        self.dest.send(data)

    def stop_forwarding(self):
        # print("...closing forwarding socket")
        self.dest.close()


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.proxy = ProxyChecker.get_instance()
        self.black_list = self.get_config()['proxy_domain']
        while not self.proxy:
            sleep(5)
            print("INFO : Waiting for proxy list to be generated...")
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
        # print("Starting to handle connection...")

        f = Forwarder(self, self.proxy.get_proxy())
        f.start()
        first_time = True
        print("Received a connection from: {}:{}".format(self.client_address[0], self.client_address[1]))
        try:
            while True:
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
                                print("Using DIRECT Connection for the request : {}:{}".format(host, port))
                                f.stop_forwarding()
                                f = Forwarder(self, [host, port])
                                f.start()
                    first_time = False
                # print("Received from source: " + str(len(data)))
                f.write_to_dest(data)
        except Exception as e:
            print("EXCEPTION reading from main socket")
            print(e)

        f.stop_forwarding()
        print("Connection Closed :{}:{}".format(self.client_address[0], self.client_address[1]))

    def write_to_source(self, data):
        # print("Sending to source: " + str(len(data)))
        self.request.send(data)

    def stop_forwarding(self):
        # print("...closing main socket")
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

    pass


if __name__ == "__main__":
    HOST, PORT = "", 8080

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running on port ", port)
    try:
        while True:
            sleep(1)
    except:
        pass
    print("...server stopping.")
    server.shutdown()
