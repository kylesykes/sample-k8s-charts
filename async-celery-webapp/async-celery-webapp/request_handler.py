import sys
import logging
import asyncio
import time
import os

from aiohttp import web
from kombu.connection import ConnectionPool
from celery import Celery

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)

# import envvars
BROKER_USER = os.getenv('BROKER_USER')
BROKER_PORT = os.getenv('BROKER_PORT')
BROKER_HOST = os.getenv('BROKER_HOST')
BROKER_PASS = os.getenv('BROKER_PASS')
PORT = os.getenv('PORT', 8080)
HOST = os.getenv('HOST', '0.0.0.0')

LOG.info('Initializing Celery')

try:
    CEL = Celery(
        'task',
        broker="pyamqp://{}:{}@{}:{}//".format(
            BROKER_USER,
            BROKER_PASS,
            BROKER_HOST,
            BROKER_PORT,
        ),
        backend='rpc://')
except Exception as e:
    LOG.exception(e) 
    


def available_queues():
    reg_tasks = CEL.control.inspect().registered_tasks()
    if not reg_tasks: 
        return []
    return list(set(
        y.rsplit('.', 1)[0]
        for x in reg_tasks.values()
        for y in x
        if y.endswith('.process')
    ))


async def handler(request):
    """Handle an incoming http request
    """
    # authorize
    if request.headers.get('X-api-key') != API_KEY:
        return web.Response(text='unauthorized', status= 401)
    
    name = request.match_info['name']
    
    # Check if name is valid
    if name not in available_queues():
        return web.json_response({
            "error": 'No such model is present',
            'available': available_queues(),
        }, status=404)

    peername = request.transport.get_extra_info('peername')
    if peername is not None:
        host, _ = peername
    else:
        host = None

    content = await request.json()

    task = CEL.send_task(
        '{}.process'.format(name),
        args=(content,),
        queue=name,
    )

    LOG.info('Starting "%s" from %s for %s', task.id, host, name)
    start_time = time.time()

    while not task.ready():
        await asyncio.sleep(0)
    response = task.get()

    LOG.info('Finished "%s" after %5.3f', task.id, time.time() - start_time)
    return web.json_response(response)


async def status_handler(req):
    """Returns Status"""
    LOG.info('status begin')
    while True:
        try:
            con = CEL.pool.acquire()
        except ConnectionPool.LimitExceeded:
            await asyncio.sleep(0)
        else:
            break

    try:
        con.connect()
    except ConnectionError:
        connected = False
    else:
        connected = con.connected
    finally:
        con.close()

    CEL.pool.release(con)

    return web.json_response({
        "web": True,
        "celery": connected,
        "ok": connected,
    }, status=200 if connected else 500)


async def get_tasks(req):
    """Return a list of tasks available via Celery"""
    LOG.info('getting tasks')
    return web.json_response(available_queues())


APP = web.Application()
APP.router.add_route('POST', '/{name}', handler)
APP.router.add_route('GET', '/status', status_handler)
APP.router.add_route('GET', '/', get_tasks)

# x-api-key
API_KEY = os.getenv('API_KEY')  # make secret at some point

access_log = logging.getLogger('aiohttp.access')
access_log.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)

stdout_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(stdout_formatter)

access_log.addHandler(stdout_handler)
LOG.addHandler(stdout_handler)

# web.run_app(APP, host=HOST, port=PORT, print=lambda x: LOG.info(x))
