import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "cinematica.log"
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Gets a named logger with console and rotating file handlers
    (handles won't stack).

    :param name: __name__ from the calling module.
    :type name: str

    :return: A configured logger instance.
    :rtype: logging.Logger
    """

    logger = logging.Logger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt=_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler (INFO and above):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Rotating file handler (DEBUG and above):
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=_LOG_FILE,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
