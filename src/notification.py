import datetime
import uuid
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Coroutine

import schedule
from log import logger


class Notification(ABC):
    def __init__(self,
                 chat_id: int = None,
                 message: str = None,
                 send_func: Callable[[], Coroutine] = None,
                 period: datetime.timedelta = None,
                 scheduler: schedule.Scheduler = None,
                 on_exit: Callable[[], Coroutine] = None,
                 uuid_key: uuid.UUID = None,
                 user_id: int = None, ):
        self.chat_id = chat_id
        self.message = message
        self.send_func = send_func
        self.period = period
        self.scheduler = scheduler
        self.on_exit = on_exit or self.stop
        self.uuid_key = uuid_key or uuid.uuid4()
        self.user_id = user_id

        self.job: schedule.Job = None

    @abstractmethod
    def _create_job(self):
        pass

    def _is_executable(self):
        return all((self.send_func is not None,
                    self.chat_id is not None,
                    self.message is not None,
                    self.scheduler is not None,
                    self.period is not None,))

    async def run(self):
        logger.trace(f"Starting notification: {self}")

        if self._is_executable():
            logger.trace(f"Start notification: {self}")
            self._create_job()
            self.scheduler.add(self.job)

    async def stop(self):
        logger.trace(f"Stop notification: {self}")

        if self.job and not self.job.done:
            await self.job.stop()

    def before(self) -> str:
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
    def __str__(self):
        return f"Timer(chat_id={self.chat_id}; uuid_key={self.uuid_key}; message={self.message}; period={self.period})"

    def __repr__(self):
        return f"Timer(chat_id={self.chat_id}; uuid_key={self.uuid_key}; message={self.message}; period={self.period})"

    def _create_job(self):
        self.job = schedule.Job(func=partial(self.send_func, chat_id=self.chat_id, text=self.message),
                                period=self.period,
                                on_exit=self.on_exit)


class Repeater(Notification):
    def __str__(self):
        return f"Repeater(chat_id={self.chat_id}; uuid_key={self.uuid_key}; message={self.message}; period={self.period})"

    def __repr__(self):
        return f"Repeater(chat_id={self.chat_id}; uuid_key={self.uuid_key}; message={self.message}; period={self.period})"

    def _create_job(self):
        self.job = schedule.Job(func=partial(self.send_func, chat_id=self.chat_id, text=self.message),
                                period=self.period,
                                on_exit=self.on_exit, repeat=True)
