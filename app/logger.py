import logging
import sys

# Log format: YYyy-mm-dd hh:mm.ss - [INFO]
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s: %(message)s"


def setup_logging():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
