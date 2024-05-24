import logging
from datetime import datetime

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=f'logs/{datetime.now().strftime("%Y-%m-%d")}.log', encoding='utf-8', mode='a+')
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
