# logging_config.py
import logging

def setup_logger():
    # Configure logging to send logs to stdout
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Create and return a logger instance
    return logging.getLogger("my_app")

# Initialize the shared logger
logger = setup_logger()
