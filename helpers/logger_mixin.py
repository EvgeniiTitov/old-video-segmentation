import logging
import sys

from config import Config


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(lineno)s: %(message)s",
    stream=sys.stdout,
    level=logging.INFO if Config.VERBOSE else logging.WARNING,
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)


class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        """Instantiates and returns a logger"""
        name = ".".join([__name__, self.__class__.__name__])
        return logging.getLogger(name)
