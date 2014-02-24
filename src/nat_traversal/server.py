__author__ = 'chrisprobst'

from types import SimpleNamespace as record
from functools import partial
from traceback import print_exc

import asyncio
from nat_traversal.util import serialize, deserialize
from nat_traversal.codes import *


@asyncio.coroutine
def send_contact_request(client_info, peer_info):
    yield from peer_info.write(REQ_CONTACT)
    yield from peer_info.write(client_info.address)


@asyncio.coroutine
def handle_requests(client_info):
    while True:
        if (yield from client_info.read()) == REQ_CONTACT:
            peer_name = yield from client_info.read()

            if peer_name not in client_info.clients:
                yield from client_info.write(ERR_PEER_NOT_FOUND)
            else:
                # Notify the peer asynchronously
                asyncio.async(send_contact_request(client_info,
                                                   client_info.clients[peer_name]))

                yield from client_info.write(OK_PEER_NOTIFIED)


@asyncio.coroutine
def handle_login(client_info):
    name = yield from client_info.read()

    if name in client_info.clients:
        yield from client_info.write(ERR_ALREADY_USED)
        return

    try:
        client_info.clients[name] = client_info
        client_info.name = name
        yield from client_info.write(OK_LOGGED_IN)
        yield from handle_requests(client_info)

    finally:
        del client_info.clients[client_info.name]


@asyncio.coroutine
def handle_connection(clients, reader, writer):
    try:
        client_info = record(write=lambda data: serialize(writer, data),
                             read=lambda: deserialize(reader),
                             address=writer.get_extra_info('peername'),
                             clients=clients)
        yield from handle_login(client_info)
    except EOFError:
        pass
    except Exception:
        print_exc()
    finally:
        writer.close()


def start_nat_traversal_server(host='0.0.0.0', port=1337):
    return asyncio.start_server(partial(handle_connection, {}),
                                host, port)

# Simply starts the traversal server
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(start_nat_traversal_server())
    loop.run_forever()