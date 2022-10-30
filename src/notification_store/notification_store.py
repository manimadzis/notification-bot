from abc import ABC, abstractmethod
from typing import List

from src.notification import Notification


class NotificationStoreError(BaseException):
    pass


class NoNotificationError(NotificationStoreError):
    pass


class NotificationStoreBase(ABC):
    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> List[Notification]:
        pass

    @abstractmethod
    async def add(self, notification: Notification):
        pass

    @abstractmethod
    async def delete(self, notification: Notification):
        pass

    @abstractmethod
    async def kill(self, notification: Notification):
        pass
