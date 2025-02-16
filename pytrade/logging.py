import inspect
import logging
import os

from isort import stream

format = "%(asctime)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(format)
log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper())

stream_handler = logging.StreamHandler()
stream_handler.setLevel(log_level)
stream_handler.setFormatter(formatter)

# Create a file handler to write logs to a file
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(log_level)
file_handler.setFormatter(formatter)

def get_logger():
    stack = inspect.stack()
    parentframe = stack[1][0]

    logger_name = "DEFAULT"

    if "self" in parentframe.f_locals:
        logger_name = parentframe.f_locals["self"].__class__.__name__
    else:
        module_info = inspect.getmodule(parentframe)
        if module_info:
            logger_name = module_info.__name__

    del parentframe
    _logger = logging.getLogger(logger_name)
    _logger.setLevel(log_level)
    _logger.addHandler(stream_handler)
    _logger.addHandler(file_handler)
    return _logger