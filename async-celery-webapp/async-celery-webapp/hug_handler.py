import hug
import logging
import time
import os
import sys

from kombu.connection import ConnectionPool
from celery import Celery
from falcon import HTTP_500

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
    

@hug.get('/status', output=hug.output_format.pretty_json)
def status():
    """Returns Status"""
    LOG.info('status begin')
    
    try:
        con = CEL.pool.acquire()
        con.connect()
        connected = con.connected
    except:
        connected = False
    finally:
        con.close()
        CEL.pool.release(con)


    if connected:
        return {
            "web": True,
            "celery": connected,
            "ok": connected,
        }
    else: 
        response.status = HTTP_500
        return {}


@hug.get('/{task_name}')
def test(task_name: str):
    task = CEL.send_task(f'{task_name}',
                        #  args=(body,),
                         queue=task_name,
    )

    LOG.info(f'Starting {task.id} from {host} for {name}')
    start_time = time.time()

    while not task.ready():
        time.sleep(0)
    response = task.get()

    LOG.info(f'Finished {task.id} after {time.time() - start_time}')
    return response