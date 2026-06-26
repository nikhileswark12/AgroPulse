import logging
import logging.handlers
import os
import sys

def configure_logging(app):
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    os.makedirs('logs', exist_ok=True)
    
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join('logs', 'agropulse.log'),
        maxBytes=5*1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger('agropulse')
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers to prevent duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

def get_logger(module_name):
    return logging.getLogger(f'agropulse.{module_name}')
