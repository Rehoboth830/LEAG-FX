"""
Shared logging setup for LEAG FX.

Every module in src/ should import get_logger() from here rather than
configuring its own logging — this keeps log format and destination
consistent across the whole project (per NFR-3.1, NFR-3.2, NFR-3.3).
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "leag_fx.log"
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Args:
        name: typically __name__ from the calling module, so log lines
              show which module produced them.

    Returns:
        A logging.Logger writing to both console and a persistent log file.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger() is called more than
    # once for the same module (e.g., during tests or reloads).
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler — INFO and above, for normal operation visibility.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler — DEBUG and above, persistent, rotates at 5MB so logs
    # don't grow forever (per NFR-3.2: must survive after the process ends).
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
