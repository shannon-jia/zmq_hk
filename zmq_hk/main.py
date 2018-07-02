# -*- coding: utf-8 -*-

"""RPS One Main Progam."""
import aiohttp
import asyncio
import aiozmq
import zmq
import async_timeout
import json
import logging
# from urllib.parse import urlparse
# from collections import namedtuple
import time
import random
# import types

log = logging.getLogger(__name__)


class Cctv:

    RELAY_KEEP_TIME = 20
    REPORT_STATUS_TIME = 10

    def __init__(self, loop=None,
                 url=None,
                 out_socket=None):
        self.loop = loop or asyncio.get_event_loop()
        self.url = url
        self.out_socket = out_socket
        self.result = []
        # self.numbers = []
        self.headers = {'content-type': 'application/json'}
        self.socket = "tcp://*:15570"
        self.pub = self.config_publisher()
        self.config_dealer()

    def config_publisher(self):
        log.info("config publisher...")
        ctx = zmq.Context()
        self.pub = ctx.socket(zmq.DEALER)
        self.pub.bind(self.socket)
        log.info("Publisher socket is: {}".format(self.socket))
        return self.pub

    def got_alarm(self, message):
        log.info('Receive Message {}'.format(message))
        self.publish(message)

    def publish(self, message):
        if self.pub:
            self.pub.send_multipart([b'SAM-CCTV',
                                      json.dumps(message).encode('utf-8')])
            log.info('message to be send: {}'.format(message))

    @asyncio.coroutine
    def go_dealer(self, addr):
        while True:
            try:
                log.info('config cctv...')
                log.info('output socket is: {}'.format(addr))
                self.dealer_identity = b'SAM-CCTV'
                self.dealer_closed = asyncio.Future()
                # self.dealer_recv = self.got_command
                self.queue = asyncio.Queue()
                self.dealer, _ = yield from aiozmq.create_zmq_connection(
                    lambda: ZmqDealerProtocol(self.queue,
                                              self.dealer_closed,
                                              self), zmq.DEALER)
                self.dealer.setsockopt(zmq.IDENTITY, self.dealer_identity)
                self.dealer.connect(addr)
                log.info('... Done!')
                # self.dealer_recv.add_done_callback(self.got_command)
            except OSError:
                log.error('Router not up retrying in 5 seconds... {}'.format(addr))
                yield from asyncio.sleep(1)
            else:
                break

    def config_dealer(self):
        self.loop.run_until_complete(self.go_dealer(self.out_socket))

    def info(self):
        return self.result

    async def got_command(self, msg):
        ''' once process one json '''
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8')
        log.info('got command: {}'.format(msg))
        try:
            if not isinstance(msg, dict):
                m = json.loads(msg)
            else:
                m = msg
        except Exception as e:
            log.error('get error command : {}'.format(e))
            return False

        cmd = m.get('cmd')
        if cmd == 'OK':
            return True
        cmd_type = m.get('type').upper()
        if cmd_type != 'CAMERA':
            return False
        self.got_alarm(m)
        if m.get("playBack"):
            return
        if isinstance(m.get("name"), list):
            for i in range(len(m.get("name"))):
                camera = m.get("name")[i][4:]
                preset = self.preset_value(m.get('args'))
                status = self.status_value(m.get('status'))
                self.preset(camera, preset, status)
            return True
        camera = m.get('name')[4:]
        preset = self.preset_value(m.get('args'))
        status = self.status_value(m.get('status'))
        self.preset(camera, preset, status)
        return True

    def preset_value(self, preset):
        if preset == "":
            return '1'
        return preset

    def status_value(self, status):
        if status == "ON" or status == "AUTO":
            return '1'
        return '0'

    async def post_data(self, session, data):
        with async_timeout.timeout(10):
            mesg = {}
            mesg.update(data)
            mesg['status'] = 400
            mesg['time_stamp'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime(time.time()))
            try:
                async with session.post('{}'.format(self.url),
                                        data=json.dumps(data),
                                        headers=self.headers) as response:
                    if response.status >= 200 and response.status < 300:
                        r_mesg = await response.json()
                        if r_mesg.get('uuid') != mesg.get('uuid'):
                            return
                        mesg['status'] = r_mesg.get('status', 400)
                    else:
                        mesg['status'] = response.status
            except Exception as e:
                log.error('post has error: {}'.format(e))
                mesg['status'] = 'cannot connect to host: {}'.format(self.url)
        if len(self.result) >= 10:
            self.result.pop(0)
        self.result.append(mesg)

    async def fetch_data(self, data):
        async with aiohttp.ClientSession() as session:
            await self.post_data(session, data)

    def preset(self, camera, preset='0', status='0'):
        if camera is None:
            return
        number = random.randint(0, 9999)
        # if number in self.numbers:
        #     return
        # self.numbers.append(number)
        data = {'uuid': str(number),
                'camera': camera,
                'preset': str(preset),
                'status': status}
        log.info("Http Server Received from /cctv:{}".format(data))
        asyncio.ensure_future(self.fetch_data(data))


class ZmqDealerProtocol(aiozmq.ZmqProtocol):

    transport = None

    def __init__(self, queue, on_close, caller):
        self.queue = queue
        self.on_close = on_close
        self.caller = caller

    def connection_made(self, transport):
        self.transport = transport

    def msg_received(self, msg):
        for i in msg:
            print(i)
            asyncio.ensure_future(self.caller.got_command(i))

    def connection_lost(self, exc):
        self.on_close.set_result(exc)
