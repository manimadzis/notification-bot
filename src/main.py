import asyncio
import datetime

from aiogram.contrib.fsm_storage.memory import MemoryStorage

import bot
import config
import log
import schedule
from notification import Timer
from notification_store import PostgresNotificationStore


async def main():
    config.load("config.yaml")
    conf = config.config
    print(conf)
    log.init(conf.log_level)

    store = PostgresNotificationStore()
    await store.init()

    await store.add(Timer(chat_id=123, period=datetime.timedelta(seconds=10), message="123"))
    print(await store.get_by_chat_id(123))

    scheduler = schedule.Scheduler()
    app_bot = bot.Bot(token=conf.telegram_token, scheduler=scheduler, aiogram_storage=MemoryStorage(),
                      store=store)

    await asyncio.gather(app_bot.start(), scheduler.run_forever())
    await store.close()


if __name__ == '__main__':
    asyncio.run(main())
