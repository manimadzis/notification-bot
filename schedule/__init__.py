import asyncio
import datetime
from typing import Coroutine, Callable


class Job:
    def __init__(self, func: Callable[[], Coroutine],
                 period: datetime.timedelta = datetime.timedelta(seconds=0),
                 repeat: bool = False,
                 on_exit: Callable[[], Coroutine] = None):
        self.func = func
        self.repeat: bool = repeat
        self.period: datetime.timedelta = period
        self.last_run: datetime.datetime = datetime.datetime.now()
        self.next_run: datetime.datetime = self.last_run + self.period
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
