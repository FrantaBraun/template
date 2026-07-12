import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.config import BASE_DIR, Settings


def configure_logging(settings: Settings) -> None:
    """Attach a daily-rotating file handler + console handler to the root logger."""
    log_dir = Path(settings.logging_dir)
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(settings.logging_message_format)

    file_handler = TimedRotatingFileHandler(
        log_dir / settings.logging_filename,
        when="midnight",
        interval=1,
        backupCount=settings.logging_days_history,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.logging_level.upper())
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    root.addHandler(file_handler)
    root.addHandler(console_handler)
