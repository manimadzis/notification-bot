import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage

import bot
import config
import log
import schedule
from notification_store import InMemoryNotificationStore


async def main():
    config.load("config.yaml")
    conf = config.config
    print(conf)
    log.init(conf.log_level)

    scheduler = schedule.Scheduler()
    app_bot = bot.Bot(token=conf.telegram_token, scheduler=scheduler, aiogram_storage=MemoryStorage(),
                      store=InMemoryNotificationStore())

    await asyncio.gather(app_bot.start(), scheduler.run_forever())


if __name__ == '__main__':
    asyncio.run(main())
