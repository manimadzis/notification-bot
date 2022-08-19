import asyncio
import datetime
from abc import ABC, abstractmethod
from functools import partial
from typing import Coroutine, Callable


class Job:
    def __init__(self, func: Callable[[], Coroutine],
                 period: datetime.timedelta = datetime.timedelta(seconds=0),
                 repeat: bool = False,
                 on_exit: Callable[[], Coroutine] = None):
        self.func = func
        self.repeat = repeat
        self.period = period
        self.last_run = datetime.datetime.now()
        self.next_run = self.last_run + self.period
        self.done = False
        self.on_exit = on_exit

    async def run(self) -> Coroutine:
        res = await self.func()
        self.last_run = datetime.datetime.now()
        self.next_run = self.next_run + self.period

        if not self.repeat:
            await self.stop()

        return res

    def need_run(self, time: datetime.datetime) -> bool:
        if self.done:
            return False
        return time >= self.next_run

    async def stop(self):
        self.done = True
        if self.on_exit:
            await self.on_exit()


class Schedule:
    def __init__(self):
        self.jobs = []

    def add(self, job: Job) -> None:
        self.jobs.append(job)

    async def run(self) -> None:
        now = datetime.datetime.now()
        jobs = [job.run() for job in self.jobs if job.need_run(now)]
        if jobs:
            await asyncio.wait(jobs)

        new_jobs = []
        for job in self.jobs:
            if not job.done:
                new_jobs.append(job)
        self.jobs = new_jobs


default = Schedule()


async def run():
    await default.run()


def add(job: Job):
    default.add(job)


class Notifier(ABC):
    def __init__(self, send_func: Callable[[], Coroutine], chat_id: int, message: str, period: datetime.timedelta,
                 on_exit: Callable[[], Coroutine] = None):
        self.period = period
        self.on_exit = on_exit
        self.job = None

        self.send_func = send_func
        self.message = message
        self.chat_id = chat_id

    @abstractmethod
    def _create_job(self):
        pass

    async def run(self):
        self._create_job()
        add(self.job)

    async def stop(self):
        if self.job:
            await self.job.stop()

    def __str__(self):
        now = datetime.datetime.now()
        next_run = self.job.next_run
        after = next_run - now
        return f"Сработает через {after.seconds} секунд. В {next_run}"


class Timer(Notifier):
    def _create_job(self):
        self.job = Job(func=partial(self.send_func, chat_id=self.chat_id, text=self.message), period=self.period,
                       on_exit=self.on_exit)


class Repeater(Notifier):
    def _create_job(self):
        self.job = Job(func=partial(self.send_func, chat_id=self.chat_id, text=self.message), period=self.period,
                       on_exit=self.on_exit, repeat=True)
