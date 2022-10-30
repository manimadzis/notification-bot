import uuid
from collections import defaultdict
from typing import Dict

from src.log import logger
from src.notification import Notification
from .error import *
from .notification_store import NotificationStoreBase


class InMemoryNotificationStore(NotificationStoreBase):
    def __init__(self):
        self.notifications: Dict[int, Dict[uuid.UUID, Notification]] = defaultdict(lambda: {})

    async def get_by_chat_id(self, chat_id: int) -> Dict[uuid.UUID, Notification]:
        logger.trace(f"Get notifications by chat_id: {chat_id}")

        return self.notifications[chat_id]

    async def add(self, notification: Notification):
        logger.trace(f"Add notification: {notification}")

        notification.uuid_key = uuid.uuid4()
        self.notifications[notification.chat_id][notification.uuid_key] = notification

    async def delete(self, notification: Notification):
        logger.trace(f"Delete notification: {notification}")

        try:
            del self.notifications[notification.chat_id][notification.uuid_key]
        except KeyError:
            raise NoNotificationError

    async def kill(self, notification: Notification):
        logger.trace(f"Stop notification: chat_id:{notification.chat_id}; notification uuid: {notification.uuid_key}")

        notification = self.notifications.get(notification.chat_id, {}).get(notification.uuid_key)
        if not notification:
            logger.error("Not found notification: chat_id:{chat_id}; notification uuid: {uuid_key}")
            return

        await notification.stop()
        await self.delete(notification)

