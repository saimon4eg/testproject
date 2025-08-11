import os
from pathlib import Path

from app.utils import safe_strtobool

DATABASE_URL = os.getenv('DATABASE_URL')

URL_PREFIX = os.getenv('URL_PREFIX', '/backend/api').rstrip('/')

# Cache
REDIS_URL = os.getenv('REDIS_URL')

# RabbitMQ
RABBITMQ_URL = os.getenv('RABBITMQ_URL')

DEBUG_MODE = safe_strtobool(os.getenv('DEBUG_MODE', 'false'))


def swagger_is_disabled() -> bool:
    return DEBUG_MODE


def root_path() -> Path:
    return Path(__file__).parent.parent
