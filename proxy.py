import socket
import select
import time
import sys

import yaml

from components.proxy_checker import ProxyChecker


class Forward(object):
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, int(port)))
            return self.forward
        except Exception as e:
            print(e)
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port=int(self.get_config()['proxy_port'])
        self.server.bind((host, port))
        self.server.listen(200)
        self.black_list=self.get_config()['proxy_domain']
        self.buffer_size = self.get_config()['buffer_size']
        self.delay = self.get_config()['delay']
        self.proxy = ProxyChecker.get_instance()
        while not self.proxy:
            time.sleep(5)
            print("INFO : Waiting for proxy list to be generated...")
            self.proxy = ProxyChecker.get_instance()
        print("INFO : Listening on {}:{}".format(host,port))

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(self.delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break
                try:
                    self.data = self.s.recv(self.buffer_size)
                except:
                    self.data=''
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        proxy=self.proxy.get_proxy()
        forward = Forward().start(proxy[0], proxy[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print(clientaddr, "has connected")
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print("Can't establish connection with remote server.")
            print("Closing connection with client side", clientaddr)
            clientsock.close()

    def on_close(self):
        try:
            print(self.s.getpeername(), "has disconnected")
        except Exception as e:
            pass
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        # print(data)
        host, port=self.get_orig_host(data)

        if host and port:
            use_proxy = False
            # Check the proxy list
            for domain in self.black_list:
                if domain in host:
                    # Continue to use forward proxy
                    use_proxy=True
                    break
            if not use_proxy:
                forward = Forward().start(host, port)
                if forward:
                    self.input_list.remove(self.channel[self.s])
                    del self.channel[self.channel[self.s]]
                    self.input_list.append(forward)
                    self.channel[self.s]=forward
                    self.channel[forward]=self.s
        # print("Host: {} Port: {}".format(host,port))
        try:
            self.channel[self.s].send(data)
        except socket.error:
            self.on_close()
        except KeyError:
            self.input_list.remove(self.s)
            self.s.close()


    def get_config(self):
        json = {}
        with open('config.yaml') as file:
            json = yaml.load(file)
        return json

    def get_orig_host(self,input):
        datas=str(input).split('\\r\\n')
        for data in datas:
            if 'Host:' in data:
                data_list=data.split(":")
                if len(data_list)==2:
                    return data_list[1].strip(), 80
                elif len(data_list)==3:
                    return data_list[1].strip(), int(data_list[2].strip())
        return None,None
