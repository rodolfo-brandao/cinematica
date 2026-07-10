"""Centralized logging configuration for the Cinematica project."""

import logging
import sys
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path


_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "cinematica.log"
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@lru_cache(maxsize=1)
def _get_console_handler() -> logging.StreamHandler:
    """
    Builds the shared console handler (INFO and above) on first use.

    :return: The process-wide console handler.
    :rtype: logging.StreamHandler
    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(fmt=_FORMAT, datefmt=_DATE_FORMAT))
    return handler


@lru_cache(maxsize=1)
def _get_file_handler() -> RotatingFileHandler:
    """
    Builds the shared rotating file handler (DEBUG and above) on first
    use. A single instance is reused by every logger: separate
    `RotatingFileHandler` objects on the same file would each track
    rollover independently, so one handler's rotation silently
    strands the others on a stale, renamed file.

    :return: The process-wide rotating file handler.
    :rtype: logging.handlers.RotatingFileHandler
    """

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        filename=_LOG_FILE,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8"
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(fmt=_FORMAT, datefmt=_DATE_FORMAT))
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Gets a named logger wired to the shared console and rotating file
    handlers.

    :param name: __name__ from the calling module.
    :type name: str

    :return: A configured logger instance.
    :rtype: logging.Logger
    """

    logger = logging.Logger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_get_console_handler())
    logger.addHandler(_get_file_handler())

    return logger
