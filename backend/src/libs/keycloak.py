from datetime import datetime
from models import ObjectNotFound
import jwt
import urllib3
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from config import get_config
from logging import getLogger
from libs.db import DBPool, db_pool
from models.user import User, UserDB, UserCreate, UserInternalUpdate

logger = getLogger('keycloak')

urllib3.disable_warnings()

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
    res = requests.get(req_url, verify=False)
    res.raise_for_status()
    data = res.json()
    return data.get('public_key')


def keycloak_init():
    global KEYCLOAK_SECRET_KEY
    if not KEYCLOAK_SECRET_KEY:
        KEYCLOAK_SECRET_KEY = download_keycloak_cert()


async def get_me(token: str = Depends(oauth2_scheme),
                 pool: DBPool = Depends(db_pool)) -> User:
    if not token or token == 'undefined':
        raise jwt.ExpiredSignatureError()
    payload = jwt.decode(
        token,
        f"-----BEGIN PUBLIC KEY-----\n"
        f"{KEYCLOAK_SECRET_KEY}\n"
        f"-----END PUBLIC KEY-----",
        algorithms=KEYCLOAK_ALGORITHM,
        options={"verify_signature": True, "verify_aud": False, "exp": True}
    )
    realm_roles = set()
    for it in payload.get('resource_access', {}).get(KEYCLOAK_CLIENT_ID, {}).get('roles', []):
        realm_roles.add(it)
    for it in payload.get('realm_access', {}).get('roles', []):
        realm_roles.add(it[1:])
    # print(realm_roles)
    async with pool.acquire_with_log('sql.keycloak') as db:
        async with db.transaction():
            try:
                user = await UserDB.get_identity(db, 'email=$2', payload['email'], realm_roles=realm_roles)
            except ObjectNotFound as e:
                user = None
            if user is None:
                user_c = UserCreate(
                    email=payload['email'],
                    name=payload['name']
                )
                await UserDB.create(db, user_c)
                user = await UserDB.get_identity(db, 'email=$2', payload['email'], realm_roles=realm_roles)
        await UserDB.update(db, user, UserInternalUpdate(
            last_logged_at=datetime.now(),
            last_realm_roles=','.join(realm_roles) if realm_roles else None,
            disabled=None
        ))
    return user