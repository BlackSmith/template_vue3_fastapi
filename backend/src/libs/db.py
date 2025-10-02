import asyncio
from typing import Callable, Optional
import loggate
import re
from asyncpg.connection import Connection
from asyncpg.protocol import Record
from asyncpg.pool import PoolAcquireContext
from pathlib import Path
from asyncpg import connect, Pool, Connection, UndefinedTableError
from asyncpg.connection import LoggedQuery


from config import get_config, to_bool

logger: loggate.Logger = loggate.getLogger('db')

DATABASE_URI = get_config('DATABASE_URI')
DATABASE_INIT = get_config('DATABASE_INIT', wrapper=to_bool)
MIGRATION_DIR = get_config('MIGRATION_DIR', wrapper=Path)
INTERFACE_TABLE = get_config('DATABASE_INTERFACE_TABLE_NAME')
POSTGRES_POOL_MIN_SIZE = get_config('POSTGRES_POOL_MIN_SIZE', wrapper=int)
POSTGRES_POOL_MAX_SIZE = get_config('POSTGRES_POOL_MAX_SIZE', wrapper=int)
POSTGRES_CONNECTION_TIMEOUT = get_config('POSTGRES_CONNECTION_TIMEOUT', wrapper=float)
POSTGRES_CONNECTION_CHECK = get_config('POSTGRES_CONNECTION_CHECK', wrapper=float)


class DBPoolAcquireContext(PoolAcquireContext):

    def __init__(self, pool, timeout, logger):
        self.logger = logger
        self.conn = None
        super().__init__(pool, timeout)

    async def process(self, query: LoggedQuery):
        fce = self.logger.error if query.exception else self.logger.debug
        fce(query.query, meta={
            'args': query.args,
            'elapsed': query.elapsed,
        })

    async def __aenter__(self) -> Connection:
        self.conn = await super().__aenter__()
        self.conn.add_query_logger(self.process)
        return self.conn

    async def __aexit__(self, *exc):
        if self.conn:
          self.conn.remove_query_logger(self.process)
        await super().__aexit__()


class DBPool(Pool):

  def acquire_with_log(self, logger, timeout=None) -> DBPoolAcquireContext:
    if isinstance(logger, str):
        logger = loggate.get_logger(logger)
    return DBPoolAcquireContext(self, timeout, logger)


class DBConnection:
    startup_callbacks = []
    notifications = {}
    singleton = None

    @classmethod
    async def get_pool(cls) -> DBPool | None:
        if not cls.singleton:
            return None
        if not cls.singleton.pool:
            await cls.singleton.start_pool()
        return cls.singleton.pool

    @classmethod
    def register_startup(cls, fce: Callable):
        cls.startup_callbacks.append(fce)

    @classmethod
    def register_notification(cls, channel: str, fce: Callable):
        cls.notifications[channel] = fce

    def __init__(self) -> None:
        self.end = False
        self.pool: Optional[DBPool] = None
        self.checking_task = None
        DBConnection.singleton = self

    async def update_db_schema(self):
        if not self.pool:
            raise Exception('Before call this method, you have to create a DB pool')

        async with self.pool.acquire_with_log(logger) as db:
            count = -1
            try:
                count = int(await db.fetchval(
                    '''
                        SELECT "value"
                        FROM "public"."config_store"
                        WHERE key = $1
                    ''',
                    "db_version"
                ) or -1)
            except UndefinedTableError:
                pass
            migs = list(MIGRATION_DIR.glob('update_*.sql'))
            migs.sort()
            for file in migs:
                f_num = int(file.stem.rsplit('_', 2)[-1])
                if f_num <= count:
                    continue
                logger.debug('Found db upgrade file %s', file)
                async with db.transaction():
                    with open(file, 'r') as f:
                        await db.execute(f.read())
                logger.info('Create the database schema')

    async def listener_handler(self, connection, pid, channel, payload):
        if not self.pool:
            raise Exception('Before call this method, you have to create a DB pool')
        try:
            async with self.pool.acquire_with_log(f'{channel}.sql.listener') as db:
                return await self.notifications[channel](db, channel, payload)
        except Exception as ex:
            logger.error('Event handler failed: %s', ex, meta={
                "channel": channel,
                "payload": payload,
                "pid": pid
            }, exc_info=True)

    async def event_listener(self):
        try:
            while not self.end:
                try:
                    logger.debug('Listener try to connect.')
                    db: Connection = await connect(
                        dsn=DATABASE_URI,
                        timeout=POSTGRES_CONNECTION_TIMEOUT
                    )
                    logger.info('Listener connected.')
                    for channel in self.notifications.keys():
                        logger.debug('Register %s listener.', channel)
                        await db.add_listener(channel, self.listener_handler)
                    while not db.is_closed() and not self.end:
                        await db.execute("SELECT 1", timeout=1)
                        await asyncio.sleep(30)
                except (TimeoutError, ConnectionRefusedError):
                    logger.debug('Listener connection timeout.')
                    await asyncio.sleep(30)
                except Exception as ex:
                    logger.error("Listener connection error", exc_info=ex)
                finally:
                    try:
                        if db:
                            await db.close(timeout=1)
                    except TimeoutError:
                        pass
        except Exception as ee:
            logger.error(ee)
        finally:
            logger.info('Listener is stopped.')

    async def start(self):
        await self.start_pool()
        if self.pool:
            if DATABASE_INIT:
                await self.update_db_schema()
            if self.startup_callbacks:
                async with self.pool.acquire_with_log(logger) as db:
                    for fce in self.startup_callbacks:
                        await fce(db)
        if self.checking_task:
            self.checking_task.cancel()
        self.checking_task = asyncio.create_task(
            self.event_listener(),
            name='db-check'
        )

    async def stop(self):
        self.end = True
        # await asyncio.sleep(1)
        if self.checking_task:
            self.checking_task.cancel()
        await self.stop_pool()

    async def stop_pool(self):
        if self.pool:
            try:
                await asyncio.wait_for(self.pool.close(), 3)
            except asyncio.TimeoutError:
                self.pool.terminate()
            self.pool = None
        logger.info('Database connection pool closed')

    async def start_pool(self):
        if self.pool:
            await self.stop_pool()
        try:
            self.pool = await DBPool(
                DATABASE_URI,
                connection_class=Connection,
                record_class=Record,
                min_size=POSTGRES_POOL_MIN_SIZE,
                max_size=POSTGRES_POOL_MAX_SIZE,
                max_queries=50000,
                loop=None,
                connect=None,
                setup=None,
                init=None,
                reset=None,
                max_inactive_connection_lifetime=300.0,
            )
            # await create_pool(
            #     dsn=DATABASE_URI,
            #     min_size=POSTGRES_POOL_MIN_SIZE,
            #     max_size=POSTGRES_POOL_MAX_SIZE,
            #     timeout=POSTGRES_CONNECTION_TIMEOUT
            # )
            logger.info(
                'Database connection pool initialized. URI: %s',
                re.sub(r':.*@', ':****@', DATABASE_URI)
            )
        except (TimeoutError, ConnectionRefusedError):
            logger.warning('Database server is unavailable.')
            await asyncio.sleep(30)


async def db_pool() -> DBPool:
    return await DBConnection.get_pool()
