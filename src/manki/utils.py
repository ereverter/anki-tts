"""
Script containing the logger setup.
"""

import logging
import os
import unicodedata
from logging.handlers import RotatingFileHandler


def setup_logger(log_file=None, name="Logger"):
    """
    Set up a logger for the whole project to use.

    :param log_file: Path to the log file. If None, the log file will be saved to the project root directory.
    :param name: Name of the logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove all handlers that might have been added previously
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()  # It's important to close the handler.

    # Setup the log file path
    if log_file is None:
        current_dir = os.path.dirname(__file__)
        project_dir = os.path.abspath(os.path.join(current_dir, ".."))
        log_file = os.path.join(project_dir, ".log")

    # Add new handler
    handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=30
    )  # 10 MB limit, keep 30 old logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def normalize_text(text: str) -> str:
    normalized_text = unicodedata.normalize("NFKC", text)
    return normalized_text.strip()
