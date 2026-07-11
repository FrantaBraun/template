import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.config import BASE_DIR, Settings

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def configure_logging(settings: Settings) -> None:
    """Attach a time-rotating file handler + console handler to the root logger."""
    log_dir = Path(settings.log_dir)
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    file_handler = TimedRotatingFileHandler(
        log_dir / "app.log",
        when=settings.log_rotation_when,
        interval=settings.log_rotation_interval,
        backupCount=settings.log_rotation_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    root.addHandler(file_handler)
    root.addHandler(console_handler)
