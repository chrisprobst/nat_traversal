__author__ = 'chrisprobst'

import unittest

import asyncio
from nat_traversal.server import start_nat_traversal_server
from nat_traversal.client import connect_to_nat_traversal_server

class TestTraversal(unittest.TestCase):

    @asyncio.coroutine
    def start_server(self):
        self.server = yield from start_nat_traversal_server()

    @asyncio.coroutine
    def shutdown_server(self):
        self.server.close()
        yield from self.server.wait_closed()

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.start_server())

    def tearDown(self):
        self.loop.run_until_complete(self.shutdown_server())

    @asyncio.coroutine
    def connect_to_server(self):
        try:
            def ping(host, port):
                call_mike('kr0e@online.de')

            call, close = yield from connect_to_nat_traversal_server('kr0e@online.de')
            call_mike, close2 = yield from connect_to_nat_traversal_server('mike@online.de', ping)

            call('mike@online.de')

            yield from asyncio.sleep(1)
        finally:
            close()
            close2()

    def test_connect(self):
        self.loop.run_until_complete(self.connect_to_server())