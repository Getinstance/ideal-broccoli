import logging
import sys

# TODO Pegar level padrão e formato de um arquivo de configuração
# Mais info em https://docs.python.org/3/library/logging.html#logging.basicConfig

format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
datefmt = "%Y-%m-%dT%H:%M:%S%z"

logging.basicConfig(
    filename="ideal_broccoli.log",
    encoding="utf-8",
    level=logging.INFO,
    format=format,
    datefmt=datefmt,
)
root_logger = logging.StreamHandler(sys.stdout)
root_logger.formatter = logging.Formatter(format, datefmt=datefmt)
logging.getLogger().addHandler(root_logger)


def get_logger(name: str) -> logging.Logger:
    """Factory de logger padrão."""
    return logging.getLogger(name)
