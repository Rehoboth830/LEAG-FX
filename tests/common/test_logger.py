"""Tests for src/common/logger.py"""

import logging

from src.common.logger import LOG_FILE, get_logger


def test_get_logger_returns_logger_instance():
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)


def test_get_logger_does_not_duplicate_handlers():
    logger_first_call = get_logger("test_no_dupes")
    handler_count_after_first = len(logger_first_call.handlers)

    logger_second_call = get_logger("test_no_dupes")
    handler_count_after_second = len(logger_second_call.handlers)

    assert handler_count_after_first == handler_count_after_second


def test_logging_writes_to_persistent_file():
    logger = get_logger("test_persistence")
    test_message = "LEAG FX logging persistence check"
    logger.info(test_message)

    assert LOG_FILE.exists()
    log_contents = LOG_FILE.read_text()
    assert test_message in log_contents
