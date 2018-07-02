#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The Application Interface."""

import logging
import asyncio
# import json
from aiohttp import web

log = logging.getLogger(__name__)


class Api(object):
    ''' Application Interface for RPS
    '''

    def __init__(self, loop, port=8099, site=None):
        loop = loop or asyncio.get_event_loop()
        self.app = web.Application(loop=loop)
        self.port = port
        self.site = site
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/logs', self.sys_info)
        self.app.router.add_post('/cctv', self.cctv_server)

    def start(self):
        # outside
        web.run_app(self.app, host='0.0.0.0', port=self.port)

    async def index(self, request):
        return web.json_response({
            'name': 'Video Driver',
            'api_version': 'V2'})

    async def sys_info(self, request):
        return web.json_response(self.site.info())

    async def cctv_server(self, request):
        r = await request.json()
        # log.info("Http Server Received from /cctv: {}".format(r))
        return web.json_response({'uuid': r.get('uuid'),
                                  'status': '8000'})
