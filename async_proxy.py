"""
A New way of implementation. Try to use asyncio to solve the issue with laggy proxy.

"""


import asyncio

from components.proxy_helper import ProxyHelper


async def handle_client(reader,writer):
    try:
        data,dest = await http_check(reader)
        if not data:
            writer.close()
            return
        helper = ProxyHelper.get_instance()
        black_list = helper.black_list
        proxy = helper.proxy
        use_proxy = False
        # print("PROXY INFO:"+proxy[0]+":"+proxy[1])
        if not proxy:
            raise Exception("No available proxy.")
        if dest:
            for site in black_list:
                if site in dest[0]:
                    use_proxy=True
        else:
            print("WARNING : Strange. It doesn't looks like a HTTP Request")
            use_proxy = True
        if use_proxy:
            remote_reader, remote_writer = await asyncio.open_connection(
                proxy[0], proxy[1])
        else:
            remote_reader, remote_writer = await asyncio.open_connection(
                dest[0], dest[1])
        pipe1 = pipe_with_predata(reader,remote_writer,data)
        pipe2 = pipe(remote_reader,writer)
        await asyncio.gather(pipe1,pipe2)
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
            raw_data = data.decode()
            # print(raw_data)
            host,port = get_orig_host(data.decode())
            if host and port:
                return data,(host,port)
            else:
                return data,None
        except UnicodeDecodeError as e:
            pass
        return data,None

async def pipe_with_predata(reader, writer,data):
    try:
        writer.write(data)
        while not reader.at_eof():
            data = await reader.read(4096)
            # print(data.decode())
            writer.write(data)
    finally:
        writer.close()


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            data = await reader.read(4096)
            # print(data.decode())
            writer.write(data)
    finally:
        writer.close()

def get_orig_host(input):
    datas = str(input).split('\r\n')
    for data in datas:
        if 'Host:' in data:
            data_list=data.split(":")
            if len(data_list)==2:
                return data_list[1].strip(), 80
            elif len(data_list)==3:
                return data_list[1].strip(), int(data_list[2].strip())
    return None,None





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
