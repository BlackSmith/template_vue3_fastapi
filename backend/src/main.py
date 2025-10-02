import jwt
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Security, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from loggate import setup_logging, getLogger

from config import get_config, to_bool
from libs.helpers import get_yaml
from libs.keycloak import get_me, keycloak_init
# from libs.socket import Socket
from libs.db import DBConnection


SOCKET_DISABLED = get_config('SOCKET_DISABLED', wrapper=bool)
FRONTEND_DIR = get_config('FRONTEND_DIR')

logging_profiles = get_yaml(get_config('LOGGING_DEFINITIONS'))
setup_logging(profiles=logging_profiles)
logger = getLogger('root')

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = DBConnection()
    await conn.start()
    try:
        yield
    finally:
        await conn.stop()



keycloak_init()
app = FastAPI(debug=get_config('DEBUG', False, wrapper=bool), root_path='', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_config('CORS_ALLOW_ORIGINS').split(','),
    allow_credentials=get_config('CORS_ALLOW_CREDENTIALS', wrapper=to_bool),
    allow_methods=get_config('CORS_ALLOW_METHODS').split(','),
    allow_headers=get_config('CORS_ALLOW_HEADERS').split(','),
)

# if not SOCKET_DISABLED:
#     socket = Socket(app)

#     @socket.event
#     async def test(sid, payload):
#         print(payload)


from endpoints.users import router as users_router
from endpoints.usergroups import router as usersgroups_router
app.include_router(users_router, prefix="/api/users")
app.include_router(usersgroups_router, prefix="/api/users-groups")


@app.get("/")
async def root():
    return FileResponse(f"{FRONTEND_DIR}/index.html")


@app.get("/api/me")
async def info_about_me(user=Security(get_me)):
    return user


@app.get("/config")
async def get_configuration():
    return {
        'url': get_config('KEYCLOAK_URL'),
        'clientId': get_config('KEYCLOAK_CLIENT_ID'),
        'realm': get_config('KEYCLOAK_REALM'),
    }


@app.exception_handler(jwt.ExpiredSignatureError)
async def validation_exception_handler(request: Request,
                                       exc: jwt.ExpiredSignatureError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=jsonable_encoder({
            "detail": "The JWT token expired.",
            "status": "False"
        }),
    )

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static")
