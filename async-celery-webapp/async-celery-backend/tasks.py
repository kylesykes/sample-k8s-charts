import os
import sys
import logging

from celery import Celery, signals
from celery.app.control import Inspect


####################
# logging
####################

# Create stdout handler
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)

# Get logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add handlers to loggers
logger.addHandler(sh)

# import envvars
BROKER_USER = os.getenv('BROKER_USER')
BROKER_PORT = os.getenv('BROKER_PORT', 5672)
BROKER_HOST = os.getenv('BROKER_HOST')
BROKER_PASS = os.getenv('BROKER_PASS')

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
    logger.info(CEL.connection())
except Exception as e:
    logger.exception(e)
    pass

@signals.celeryd_init.connect
def setup_worker(*args, **kwargs):
    """Setup Worker"""
    logger.info('starting worker setup now')

    # do something

    logger.info('worker setup complete')


@CEL.task(name='samplequeuename.process')
def hello_world(request):
    """Respond with printing Hello World"""
    logger.info('initializing samplequeuename task')
    return "Hello World"