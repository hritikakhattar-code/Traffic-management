import logging
import os
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """
    Setup a logger instance
    
    Args:
        name (str): Logger name
        log_file (str): Path to log file
        level (int): Logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create directory for log file if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger
