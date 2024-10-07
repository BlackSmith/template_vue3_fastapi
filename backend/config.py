import os
import logging
from typing import Callable

DEFAULT_CONFIG = {
    'API_URL': '/api',
    'FRONTEND_DIR': './static',
    'KEYCLOAK_URL': 'https://keycloak/auth/',
    'KEYCLOAK_CLIENT_ID': 'CLIENT',
    'KEYCLOAK_REALM': 'REALM',
    'KEYCLOAK_ALGORITHM': 'RS256',
    'KEYCLOAK_SECRET_KEY': None,
    'LOGGING_DEFINITIONS': 'logging.yml',
    'LOG_LEVEL': logging.DEBUG,
    'DATABASE_URI': 'postgres://user:password@localhost:5432/db',
    'SOCKET_DISABLED': False,
    'SOCKET_RECONNECT': 10,  # seconds
}


def get_config(name: str, default=None, wrapper: Callable = None):
    if not wrapper:
        wrapper = lambda x: x   # NOQA
    return wrapper(os.getenv(name, DEFAULT_CONFIG.get(name, default)))


_logname_to_level = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def log_level(name):
    if isinstance(name, int):
        return name
    return _logname_to_level.get(name.upper(), logging.INFO)
