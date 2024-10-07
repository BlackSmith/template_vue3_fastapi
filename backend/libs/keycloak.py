import jwt
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from config import get_config
from loggate import get_logger

logger = get_logger('keycloak')

KEYCLOAK_URL = get_config('KEYCLOAK_URL')
KEYCLOAK_REALM = get_config('KEYCLOAK_REALM')
KEYCLOAK_CLIENT_ID = get_config('KEYCLOAK_CLIENT_ID')
KEYCLOAK_ALGORITHM = get_config('KEYCLOAK_ALGORITHM').split(' ')
KEYCLOAK_SECRET_KEY = get_config('KEYCLOAK_SECRET_KEY')

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl=f'{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}'
             f'/protocol/openid-connect/token',
    authorizationUrl=f'{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}'
                     f'/protocol/openid-connect/auth',
    # scopes={
    #      'email': 'Grants read access to a user\'s email addresses.'
    #  }
)


def download_keycloak_cert():
    req_url = f'{KEYCLOAK_URL}realms/{KEYCLOAK_REALM}'
    logger.warning('Missing KEYCLOAK_SECRET_KEY in config. '
                   'It will be downloaded from %s', req_url)
    import requests
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    res = requests.get(req_url, verify=False)
    res.raise_for_status()
    data = res.json()
    return data.get('public_key')


def keycloak_init():
    global KEYCLOAK_SECRET_KEY
    if not KEYCLOAK_SECRET_KEY:
        KEYCLOAK_SECRET_KEY = download_keycloak_cert()


async def get_me(token: str = Depends(oauth2_scheme)) -> dict:
    """
    :raise jose.exceptions.ExpiredSignatureError
    :param token:
    :return: dict
    :raise ExpiredSignatureError
    """
    return jwt.decode(
        token,
        f"-----BEGIN PUBLIC KEY-----\n"
        f"{KEYCLOAK_SECRET_KEY}\n"
        f"-----END PUBLIC KEY-----",
        algorithms=KEYCLOAK_ALGORITHM,
        options={"verify_signature": True, "verify_aud": False, "exp": True}
    )
