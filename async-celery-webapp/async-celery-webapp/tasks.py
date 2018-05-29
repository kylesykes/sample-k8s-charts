


@CEL.task(name='myroute.process')
def process(request):
    """Respond with MyRoute response"""
    logger.info('initializing myroute task')
    if not PCM.models_loaded():
        logger.info('something broke, raising Exception')
        raise BaseException
    return PCM.http_handler(request)
