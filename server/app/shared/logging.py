import logging

logging.getLogger('werkzeug').disabled = True
# logging.getLogger('stem').disabled = True
logging.getLogger('peewee').disabled = True
logging.getLogger('engineio.server').disabled = True

def initialize_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%H:%M:%S',
        format='%(name)s | [%(levelname)s] %(asctime)s.%(msecs)03d %(message)s'
    )