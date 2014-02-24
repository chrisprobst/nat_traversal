__author__ = 'chrisprobst'

from pickle import dumps, loads
from struct import pack, unpack

import asyncio


@asyncio.coroutine
def serialize(writer, data):
    try:
        body = dumps(data)
        header = pack('!i', len(body))
        assert len(header) == 4, 'Int is not 4 bytes long on this platform'
        writer.write(header + body)
        yield from writer.drain()
    except ConnectionResetError:
        pass


@asyncio.coroutine
def deserialize(reader):
    header = unpack('!i', (yield from reader.readexactly(4)))[0]
    body = loads((yield from reader.readexactly(header)))
    return body