import logging
import sys
import os


LOG_FILE_ENABLED = os.getenv("LOG_FILE_ENABLED", None)
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/ideal_broccoli.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
datefmt = "%Y-%m-%dT%H:%M:%S%z"

# Mais info em https://docs.python.org/3/library/logging.html#logging.basicConfig
logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG if not LOG_LEVEL else getattr(logging, LOG_LEVEL),
    format=format,
    datefmt=datefmt,
    handlers=[
        (logging.StreamHandler(sys.stdout)),
        (
            logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
            if LOG_FILE_ENABLED
            else logging.NullHandler()
        ),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Factory de logger padrão."""
    return logging.getLogger(name)
