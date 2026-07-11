import logging
from logging.handlers import TimedRotatingFileHandler

from app.config import Settings
from app.logging_config import configure_logging


def test_configure_logging_attaches_timed_rotating_handler(tmp_path):
    settings = Settings(
        log_dir=str(tmp_path),
        log_level="DEBUG",
        log_rotation_when="midnight",
        log_rotation_interval=1,
        log_rotation_backup_count=3,
    )

    configure_logging(settings)

    root = logging.getLogger()
    timed_handlers = [h for h in root.handlers if isinstance(h, TimedRotatingFileHandler)]
    assert len(timed_handlers) == 1
    assert timed_handlers[0].when == "MIDNIGHT"
    assert timed_handlers[0].backupCount == 3
    assert (tmp_path / "app.log").exists()


def test_configure_logging_writes_to_log_file(tmp_path):
    settings = Settings(log_dir=str(tmp_path), log_level="INFO")
    configure_logging(settings)

    logging.getLogger("test.logger").info("hello from test")

    log_content = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "hello from test" in log_content
