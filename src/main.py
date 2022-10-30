import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage

import bot
import config
import log
import schedule
from notification_store import InMemoryNotificationStore


async def main():
    config.load("config.yaml")
    log.init()

    scheduler = schedule.Scheduler()
    app_bot = bot.Bot(token=config.config.telegram_token, scheduler=scheduler, aiogram_storage=MemoryStorage(),
                      store=InMemoryNotificationStore())

    await asyncio.gather(app_bot.start())


if __name__ == '__main__':
    asyncio.run(main())
