import json
import jwt
from fastapi import FastAPI, Request, Security, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.encoders import jsonable_encoder

from loggate import setup_logging
from config import get_config
from libs.helpers import get_yaml
from libs.keycloak import get_me, keycloak_init
from libs.socket import Socket


SOCKET_DISABLED = get_config('SOCKET_DISABLED', wrapper=bool)
FRONTEND_DIR = get_config('FRONTEND_DIR')
JS_CONFIGS = {
    'KEYCLOAK_URL': get_config('KEYCLOAK_URL'),
    'KEYCLOAK_CLIENT_ID': get_config('KEYCLOAK_CLIENT_ID'),
    'KEYCLOAK_REALM': get_config('KEYCLOAK_REALM'),
    'API_URL': get_config('API_URL'),
    'SOCKET_DISABLED': SOCKET_DISABLED,
    'SOCKET_RECONNECT': get_config('SOCKET_RECONNECT', 'float')
}


logging_profiles = get_yaml(get_config('LOGGING_DEFINITIONS'))
setup_logging(profiles=logging_profiles)
keycloak_init()
app = FastAPI(root_path='/api')

if not SOCKET_DISABLED:
    socket = Socket(app)

    @socket.event
    async def test(sid, payload):
        print(payload)


@app.get("/")
async def root():
    return FileResponse(f"{FRONTEND_DIR}/index.html")


@app.get("/me")
async def get_me(user=Security(get_me)):
    return user


@app.get("/config.js")
async def get_me():
    res = []
    for it, val in JS_CONFIGS.items():
        val = json.dumps(val)           # We add quote and escape.
        res.append(f'const {it}={val};')
    return PlainTextResponse(
        content='\n'.join(res),
        media_type='text/javascript'
    )


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
