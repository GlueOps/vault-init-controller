import logging
from utils.json_log_formatter import JsonFormatter
import os


#=== configure logging
# json formatter
json_formatter = JsonFormatter()

# stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(json_formatter)
stream_handler.setLevel(os.getenv(
    'PYTHON_LOG_LEVEL',
    'INFO'
))

# configure logger
logger = logging.getLogger('VAULT_INIT')
logger.setLevel(os.getenv(
    'PYTHON_LOG_LEVEL',
    'INFO'
))
logger.addHandler(stream_handler)
