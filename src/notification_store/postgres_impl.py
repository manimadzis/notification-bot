from typing import List

import aiopg
import psycopg2.extras

from src.log import logger
from src.notification import Notification, Timer, Repeater
from .notification_store import NotificationStoreBase


class PostgresNotificationStore(NotificationStoreBase):
    def __init__(self,
                 *,
                 host: str = "localhost",
                 post: str = "5432",
                 username: str = "postgres",
                 password: str = "postgres",
                 database: str = "postgres",
                 max_pool_size: int = 100):

        self._max_pool_size = max_pool_size
        self._dsn = f"host={host} user={username} password={password} dbname={database}"
        self._conn: aiopg.Connection = None

    async def _create_db(self):
        await self._exec("""CREATE TABLE IF NOT EXISTS notification(
        uuid_key UUID PRIMARY KEY,
        chat_id INT NOT NULL,
        message TEXT NOT NULL,
        period INTERVAL NOT NULL,
        "type" TEXT NOT NULL,
        "time" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

    async def _exec(self, query, *params, **kwparams) -> aiopg.Cursor:
        async with self._conn.cursor() as cur:
            if params:
                await cur.execute(query, parameters=params)
            elif kwparams:
                await cur.execute(query, parameters=kwparams)
            else:
                await cur.execute(query, )
        return cur

    async def get_by_chat_id(self, chat_id: int) -> List[Notification]:
        async with self._conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            await cur.execute(f"""SELECT *
             FROM notification 
             WHERE chat_id = {chat_id}""")
            notifications = []
            async for row in cur:
                if row.type == "Timer":
                    notification = Timer(chat_id=row.chat_id,
                                         message=row.message,
                                         uuid_key=str(row.uuid_key),
                                         period=row.period)
                elif row.type == "Repeater":
                    notification = Repeater(chat_id=row.chat_id,
                                            message=row.message,
                                            uuid_key=str(row.uuid_key),
                                            period=row.period)
                else:
                    logger.error(f"Unknown type: {row.type}")
                    continue

                notifications.append(notification)
        return notifications

    async def add(self, notification: Notification):
        logger.info(f"Add notification: {notification}")
        notification_type = type(notification).__name__
        try:
            await self._exec("""INSERT INTO notification(
                uuid_key,
                chat_id,
                message,
                period,
                \"type\") 
                VALUES(%s, %s, %s, %s, %s)""",
                             notification.uuid_key,
                             notification.chat_id,
                             notification.message,
                             notification.period,
                             notification_type)
        except Exception as e:
            logger.exception(e)

    async def delete(self, notification: Notification):
        logger.info(f"Delete notification: {notification}")
        await self._exec("DELETE FROM notification WHERE uuid_key = %s", notification.uuid_key)

    async def kill(self, notification: Notification):
        logger.info(f"Kill notification: {notification}")
        await self.delete(notification)
        await notification.stop()

    async def init(self):
        logger.info("Init postgres DB")
        self._conn = await aiopg.connect(self._dsn)
        await self._create_db()

    async def __aexit__(self):
        await self._conn.close()

    async def close(self):
        await self._conn.close()
