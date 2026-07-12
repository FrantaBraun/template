# Part of the With FBraun project template.
# Author: František Braun <frantisek.braun95@gmail.com>
# Freely available as a template for building custom applications.

"""Tests for app.logging_config.configure_logging: handler wiring, actual
writes to the log file, and custom message formatting."""

import logging
from logging.handlers import TimedRotatingFileHandler

from app.config import Settings
from app.logging_config import configure_logging


def test_configure_logging_attaches_timed_rotating_handler(tmp_path):
    settings = Settings(
        logging_dir=str(tmp_path),
        logging_level="DEBUG",
        logging_filename="custom.log",
        logging_days_history=3,
    )

    configure_logging(settings)

    root = logging.getLogger()
    timed_handlers = [h for h in root.handlers if isinstance(h, TimedRotatingFileHandler)]
    assert len(timed_handlers) == 1
    assert timed_handlers[0].when == "MIDNIGHT"
    assert timed_handlers[0].backupCount == 3
    assert (tmp_path / "custom.log").exists()


def test_configure_logging_writes_to_log_file(tmp_path):
    settings = Settings(logging_dir=str(tmp_path), logging_level="INFO")
    configure_logging(settings)

    logging.getLogger("test.logger").info("hello from test")

    log_content = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "hello from test" in log_content


def test_configure_logging_uses_custom_message_format(tmp_path):
    settings = Settings(
        logging_dir=str(tmp_path),
        logging_level="INFO",
        logging_message_format="CUSTOM|%(levelname)s|%(message)s",
    )
    configure_logging(settings)

    logging.getLogger("test.logger").info("formatted message")

    log_content = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "CUSTOM|INFO|formatted message" in log_content
