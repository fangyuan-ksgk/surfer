import logging
import logging.config
import sys
from pathlib import Path

from rich.logging import RichHandler

from .directories import LOGS_DIR

# Loggers configuration
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "minimal": {"format": "%(message)s"},
        "detailed": {
            "format": "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "detailed",
            "level": logging.INFO,
        },
        "info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "info.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.INFO,
            "encoding": "utf-8",
        },
        "error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "error.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.ERROR,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "info", "error"],
            "level": logging.INFO,
            "propagate": True,
        },
        "uvicorn": {
            "handlers": ["console", "info", "error"],
            "level": logging.DEBUG,
            "propagate": False,
        },
    },
}

logging.config.dictConfig(logging_config)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("root")
logger.handlers[0] = RichHandler(markup=True, log_time_format="%Y-%m-%d %H.%M.%S.%f")
