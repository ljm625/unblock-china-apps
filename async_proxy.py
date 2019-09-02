"""
A New way of implementation. Try to use asyncio to solve the issue with laggy proxy.

"""


import asyncio
import aiosocks
from components.proxy_helper import ProxyHelper


async def handle_client(reader,writer):
    # Add HTTPS support (Connect proxy.)
    try:
        data,dest,https = await http_check(reader)
        if not data:
            writer.close()
            return
        helper = ProxyHelper.get_instance()
        black_list = helper.black_list
        proxy = helper.proxy
        use_proxy = False
        # print("Proxy Got from Server: {}:{}".format(proxy[0],proxy[1]))
        if not proxy:
            raise Exception("No available proxy.")
        if dest:
            for site in black_list:
                if site in dest[0]:
                    use_proxy=True
        elif helper.always_use_proxy:
            use_proxy=True
        else:
            print("WARNING : Strange. It doesn't looks like a HTTP Request")
            use_proxy = True
        if use_proxy:
            try:
                if proxy[2]=='SOCKS5':
                    socks5_addr = aiosocks.Socks5Addr(proxy[0],proxy[1])
                    # socks5_auth = aiosocks.Socks5Auth(login="",password="")

                    remote_reader, remote_writer = await aiosocks.open_connection(
                        proxy=socks5_addr, dst=[dest[0],dest[1]], remote_resolve=True,proxy_auth=None)
                else:
                    remote_reader, remote_writer = await asyncio.open_connection(
                    proxy[0], proxy[1])
            except ConnectionRefusedError as e:
                print("Connect to proxy failed.")
                writer.close()
                helper.params['fetch']=True
                return
        elif helper.disable_proxy:
            writer.close()
            return
        else:
            remote_reader, remote_writer = await asyncio.open_connection(
                dest[0], dest[1])
        if not use_proxy and https:
            https_respond(writer)
            pipe1 = pipe(reader, remote_writer)
            pipe2 = pipe(remote_reader, writer)
            await asyncio.gather(pipe1, pipe2)
            return
        pipe1 = pipe_with_predata(reader,remote_writer,data)
        pipe2 = pipe(remote_reader,writer)
        await asyncio.gather(pipe1,pipe2)
    except Exception as e:
        print("Exception in Async Process: {}".format(e))
        if "Connection reset" in str(e):
            helper.params['fetch'] = True
            print("Trying to find new server.")



    finally:
        writer.close()
    #     data = await reader.read(100)
    #     message=data.decode()
    #     print(message)
    #
    # writer.write(data)
    # await writer.drain() # wait until the write is complete.
    # writer.close()

async def http_check(reader):
    if not reader.at_eof():
        data = await reader.read(4096)
        try:
            # raw_data = data.decode()
            # print(raw_data)
            host,port,https = get_orig_host(data.decode())
            if host and port:
                return data,(host,port),https
            else:
                return data,None,https
        except UnicodeDecodeError as e:
            pass
        return data,None,False

async def pipe_with_predata(reader, writer,data):
    try:
        writer.write(data)
        while not reader.at_eof():
            data = await reader.read(4096)
            # print(data.decode())
            writer.write(data)
    finally:
        writer.close()

def https_respond(writer):
    # try:
        reply = "HTTP/1.0 200 Connection established\r\n"
        reply += "Proxy-agent: Pyx\r\n"
        reply += "\r\n"
        writer.write(reply.encode())
    # finally:
    #     writer.close()

async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            data = await reader.read(4096)
            # print(data.decode())
            writer.write(data)
    finally:
        writer.close()

def get_orig_host(input):
    https=False
    if "CONNECT" in str(input):
        https=True
    datas = str(input).split('\r\n')
    for data in datas:
        if 'Host:' in data:
            data_list=data.split(":")
            if len(data_list)==2:
                return data_list[1].strip(), 80,https
            elif len(data_list)==3:
                return data_list[1].strip(), int(data_list[2].strip()),https
    return None,None,https





# if __name__ == '__main__':
#     loop=asyncio.get_event_loop()
#     coro = asyncio.start_server(handle_client, '127.0.0.1', 8888,loop=loop)
#     server = loop.run_until_complete(coro)
#
#     print('Serving on {}'.format(server.sockets[0].getsockname()))
#
#     try:
#         loop.run_forever()
#     except KeyboardInterrupt:
#         pass
#
#     # Close the server
#     server.close()
#     loop.run_until_complete(server.wait_closed())
#     loop.close()
