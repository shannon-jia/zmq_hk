# -*- coding: utf-8 -*-

import click
# import logging
from .log import get_log
from .api import Api
from .main import Cctv
import asyncio

def validate_url(ctx, param, value):
    try:
        return value
    except ValueError:
        raise click.BadParameter('url need to be format: tcp://ipv4:port')

@click.command()
@click.option('--cctv_url', default='http://127.0.0.1:8099/cctv',
              callback=validate_url,
              envvar='CCTV_URL',
              help='CCTV Server url, ENV: CCTV_URL')
@click.option('--api', default=8099,
              envvar='RPS_PORT',
              help='Api port, default=8099, ENV: RPS_PORT')
@click.option('--debug', is_flag=True)
@click.option('--out_socket', default='tcp://127.0.0.1:5570',
              help='Zmq Server router.')

def main(cctv_url, api,  debug, out_socket):
    """Keeper for SAM2"""

    click.echo("See more documentation at http://www.mingvale.com")

    info = {
        'cctv_url': cctv_url,
        'out_socket': out_socket,
        'api': api
    }

    log = get_log(debug)
    log.info('Basic Information: {}'.format(info))

    loop = asyncio.get_event_loop()
    loop.set_debug(0)
    try:
        site = Cctv(loop, cctv_url, out_socket)
        api = Api(loop=loop, port=api, site=site)
        api.start()
        loop.run_forever()
    except KeyboardInterrupt:
        site.stop()
    finally:
        loop.stop()
        loop.close()
