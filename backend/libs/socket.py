import jwt
from typing import Union

from fastapi import FastAPI
from socketio.async_server import AsyncServer
from socketio.asgi import ASGIApp
from loggate import getLogger

from libs.keycloak import get_me


# class SocketError(Exception):
#     def __init__(self, *args, sid=None, event_name='', **kwargs):
#         super().__init__(*args, **kwargs)
#         self.sid = sid
#         self.event_name = event_name


class Socket(AsyncServer):

    def __init__(self, app: FastAPI, socketio_path: str = "socket.io",
                 cors_allowed_origins: Union[str, list] = '*', **kwargs):
        super().__init__(
            async_mode='asgi',
            cors_allowed_origins=cors_allowed_origins,
            **kwargs
        )
        self._app = ASGIApp(socketio_server=self, socketio_path=socketio_path)
        app.mount(f'/{socketio_path}', self._app)
        app.socket = self
        self.logger = getLogger(self.__class__.__name__)
        self.on('connect', self.on_connect)
        self.on('disconnect', self.on_disconnect)

    async def disconnect(self, sid, namespace=None, ignore_queue=False,
                         reason=None):
        if reason:
            await self.emit('disconnect_reason', {'reason': reason},
                            to=sid)
        await super().disconnect(sid, namespace, ignore_queue)

    async def on_connect(self, sid, environ, *args):
        self.logger.info(
            f'New user {sid} ({environ["REMOTE_ADDR"]}) connected.'
        )

        # import pprint
        # pprint.pprint(environ)
        # we save user IP to local session
        if not sid:
            return False
        async with self.session(sid) as session:
            session['ip'] = environ["REMOTE_ADDR"]
            if args:
                try:
                    session['user'] = await get_me(args[0].get('token', ''))
                except jwt.ExpiredSignatureError as e:
                    self.logger.warning(e)
                    await self.disconnect(sid, reason='token-expired')

    async def on_disconnect(self, sid, reason=''):
        async with self.session(sid) as session:
            self.logger.info(f'User {sid} ({session["ip"]}) disconnected. '
                             f'Reason: {reason}')
