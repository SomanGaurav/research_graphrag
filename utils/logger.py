import logging
import os 
from logging.handlers import RotatingFileHandler 

def setup_logger(logger_name="graphrag_logger"):
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "applogs")
    os.makedirs(log_dir, exist_ok=True) 

    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers(): 
        return logger 
    
    console_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s', 
        datefmt='%H:%M:%S'
    )

    file_format = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_format)
    log_file_path = os.path.join(log_dir, 'agent_system.log')
    file_handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8' 
    )
    
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

app_logger = setup_logger()


