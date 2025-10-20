import logging
import sys
import os


LOG_FILE_ENABLED = os.getenv("LOG_FILE_ENABLED", False)
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/ideal_broccoli.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
datefmt = "%Y-%m-%dT%H:%M:%S%z"

# Mais info em https://docs.python.org/3/library/logging.html#logging.basicConfig
logging.basicConfig(
    filename=LOG_FILE_PATH if LOG_FILE_ENABLED else None,
    encoding="utf-8",
    level=logging.DEBUG if not LOG_LEVEL else getattr(logging, LOG_LEVEL),
    format=format,
    datefmt=datefmt,
)

root_logger = logging.StreamHandler(sys.stdout)
root_logger.formatter = logging.Formatter(format, datefmt=datefmt)

logging.getLogger().addHandler(root_logger)


def get_logger(name: str) -> logging.Logger:
    """Factory de logger padrão."""
    return logging.getLogger(name)
