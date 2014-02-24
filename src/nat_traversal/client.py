__author__ = 'chrisprobst'

import asyncio
from nat_traversal.util import serialize, deserialize
from nat_traversal.codes import *


@asyncio.coroutine
def connect_to_nat_traversal_server(name, contact_cb = None, host='localhost', port=1337):
    """
    Connects to the nat traversal server and starts listening for contact
    requests.

    Returns a pair of functions: (send_contact(name), close())
    """
    reader, writer = yield from asyncio.open_connection(host, port)
    read, write = lambda: deserialize(reader), lambda data: serialize(writer, data)

    @asyncio.coroutine
    def process_contact_requests():
        try:
            while True:
                req = yield from read()
                if req == REQ_CONTACT:
                    address = yield from read()
                    if contact_cb:
                        contact_cb(*address)
                    print('[%s], Received contact request: Host=%s Port=%s' % ((name,) + address))
        except EOFError:
            pass
        finally:
            writer.close()

    @asyncio.coroutine
    def send_contact_request(name):
        yield from write(REQ_CONTACT)
        yield from write(name)

    yield from write(name)
    login_result = yield from read()

    if login_result != OK_LOGGED_IN:
        raise KeyError('Name=%s is already taken' % name)

    asyncio.async(process_contact_requests())

    return (lambda peer_name: asyncio.async(send_contact_request(peer_name)),
            lambda: writer.close())
