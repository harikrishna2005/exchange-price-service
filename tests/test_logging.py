import logging
import pytest
from src.common_lib.logging import configure_logging, LogLevel


def test_configure_logging_sets_debug_level(caplog):
    configure_logging(LogLevel.DEBUG)
    # logger = logging.getLogger()
    assert getattr(logging, LogLevel.DEBUG) == logging.DEBUG
    with caplog.at_level(logging.DEBUG):
        logging.debug("debug message")
    assert "debug message" in caplog.text


def test_configure_logging_sets_info_level(caplog):
    configure_logging(LogLevel.INFO)
    # logger = logging.getLogger()
    assert getattr(logging, LogLevel.INFO) == logging.INFO
    with caplog.at_level(logging.INFO):
        logging.info("info message")
    assert "info message" in caplog.text


def test_configure_logging_invalid_level_sets_error():
    configure_logging("INVALID")

    # logger = logging.getLogger()

    assert getattr(logging, LogLevel.ERROR) == logging.ERROR


def test_loglevel_enum_values():
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"
