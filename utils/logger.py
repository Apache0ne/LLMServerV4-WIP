# utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(config):
    log_level = getattr(logging, config.get('level', 'INFO'))
    log_file = config.get('file', 'llmserver.log')
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),
            logging.StreamHandler()
        ]
    )

def get_logger(name):
    return logging.getLogger(name)