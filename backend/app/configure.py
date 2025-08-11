import logging
from logging.config import dictConfig

from .settings.logger import config as logger_config

logger = logging.getLogger(__name__)


def configure():

    # Logger
    dictConfig(logger_config)
    logging.basicConfig(level=logging.ERROR)
