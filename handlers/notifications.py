import datetime
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import partial
from typing import Dict, Callable, Coroutine

import schedule


class NotificationStore:
    pass


class Notification(ABC):
    class NotifierMemento:
        def __init__(self, send_func: Callable[[], Coroutine], chat_id: int, message: str, period: datetime.timedelta,
                     on_exit: Callable[[], Coroutine] = None):
            self.period = period
            self.on_exit = on_exit
            self.send_func = send_func
            self.message = message
            self.chat_id = chat_id

    def __init__(self, send_func: Callable[[], Coroutine], chat_id: int, message: str, period: datetime.timedelta,
                 on_exit: Callable[[], Coroutine] = None, store: NotificationStore = None):
        self.period = period
        self.on_exit = on_exit or self.stop
        self.job = None

        self.send_func = send_func
        self.message = message
        self.chat_id = chat_id
        self.store = store or default_store
        self.uuid_key = None

    @abstractmethod
    def _create_job(self):
        pass

    async def run(self):
        self._create_job()
        schedule.add(self.job)
        self.store.add(self)

    async def stop(self):
        if self.job and not self.job.done:
            await self.job.stop()
        self.store.delete(self.chat_id, self.uuid_key)

    def before(self):
        now = datetime.datetime.now()
        next_run = self.job.next_run
        after = next_run - now

        str_next_run = next_run.strftime("%H:%M:%S %m/%d/%Y")

        if after.seconds < 60:
            return f"Сработает через {after.seconds} секунд. В {str_next_run}"

        minutes = after.seconds // 60
        seconds = after.seconds % 60

        if minutes < 60:
            return f"Сработает через {minutes} минут и {seconds} секунд. В {str_next_run}"

        hours = minutes // 60
        minutes = minutes % 60

        return f"Сработает через {hours} часов и {minutes} минут. В {str_next_run}"


class Timer(Notification):
    def _create_job(self):
        self.job = schedule.Job(func=partial(self.send_func, chat_id=self.chat_id, text=self.message),
                                period=self.period,
                                on_exit=self.on_exit)


class Repeater(Notification):
    def _create_job(self):
        self.job = schedule.Job(func=partial(self.send_func, chat_id=self.chat_id, text=self.message),
                                period=self.period,
                                on_exit=self.on_exit, repeat=True)


class NotificationStore:
    def __init__(self):
        self.notifications: Dict[int, Dict[uuid.UUID, Notification]] = defaultdict(lambda: {})

    def get(self, chat_id: int) -> Dict[uuid.UUID, Notification]:
        return self.notifications[chat_id]

    def add(self, notification: Notification):
        uuid_key = uuid.uuid4()
        self.notifications[notification.chat_id][uuid_key] = notification
        notification.uuid_key = uuid_key

    def delete(self, chat_id: int, uuid_key: uuid.UUID):
        try:
            del self.notifications[chat_id][uuid_key]
        except:
            pass

    async def kill(self, chat_id: int, uuid_key: uuid.UUID):
        notification = self.notifications.get(chat_id, {}).get(uuid_key)
        if not notification:
            return

        await notification.stop()


default_store = NotificationStore()


def get(chat_id: int) -> Dict[uuid.UUID, Notification]:
    return default_store.get(chat_id)


def add(notification: Notification):
    default_store.add(notification)


def delete(chat_id: int, uuid_key: uuid.UUID):
    default_store.delete(chat_id, uuid_key)


async def kill(chat_id: int, uuid_key: uuid.UUID):
    await default_store.kill(chat_id, uuid_key)
