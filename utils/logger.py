import logging
from datetime import datetime
import os

def setup_logger():
    # /tmp/logs 디렉토리가 존재하지 않으면 생성
    if not os.path.exists('/tmp/logs'):
        os.makedirs('/tmp/logs')
    
    # 로그 파일을 /tmp/logs 디렉토리에 생성
    handler = logging.FileHandler(filename=f'/tmp/logs/{datetime.now().strftime("%Y-%m-%d")}.log', encoding='utf-8', mode='a+')
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger
