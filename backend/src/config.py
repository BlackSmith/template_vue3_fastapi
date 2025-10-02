import os
import logging
from typing import Any, Callable

DEFAULT_CONFIG = {
    'API_URL': '/api',
    'FRONTEND_DIR': './static',
    'KEYCLOAK_URL': 'https://keycloak/auth/',
    'KEYCLOAK_CLIENT_ID': 'CLIENT',
    'KEYCLOAK_REALM': 'REALM',
    'KEYCLOAK_ALGORITHM': 'RS256',
    'KEYCLOAK_SECRET_KEY': None,
    'KEYCLOAK_REALM_ADMIN_ROLE': 'APP_ADMIN_ROLE',
    'LOGGING_DEFINITIONS': 'logging.yml',
    'LOG_LEVEL': logging.DEBUG,
    'PERMISSION_DEFINITIONS': 'permissions.yml',
    'DATABASE_URI': 'postgres://user:password@localhost:5432/db',
    'DATABASE_INIT': 'yes',
    'POSTGRES_POOL_MIN_SIZE': 5,
    'POSTGRES_POOL_MAX_SIZE': 10,
    'POSTGRES_CONNECTION_TIMEOUT': 5,
    'POSTGRES_CONNECTION_CHECK': 5,
    'MIGRATION_DIR': 'migration/',
    'CORS_ALLOW_ORIGINS': '*',  # comma separated
    'CORS_ALLOW_METHODS': '*',  # comma separated
    'CORS_ALLOW_HEADERS': '*',  # comma separated
    'CORS_ALLOW_CREDENTIALS': 'yes',

    'SOCKET_DISABLED': False,
    'SOCKET_RECONNECT': 10,  # seconds
}


def get_config(name: str, default: Any = None, wrapper: Callable | None = None):
    if not wrapper:
        wrapper = lambda x: x   # NOQA
    return wrapper(os.getenv(name, DEFAULT_CONFIG.get(name, default)))


def to_bool(val) -> bool:
    return str(val).upper() in ['1', 'Y', 'YES', 'T', 'TRUE']


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
