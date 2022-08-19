import asyncio
import os

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

import schedule
from handlers import register_handlers


async def schedule_main():
    while True:
        await schedule.run()
        await asyncio.sleep(1)


async def set_commands_helper(bot: Bot):
    commands = [
        BotCommand("/start", "начать работу с ботом, вернуться в меню"),
        BotCommand("/timer", "запустить таймер"),
        BotCommand("/repeater", "запустить повторитель"),
        BotCommand("/stop", "остановить"),
        BotCommand("/help", "помощь")
    ]
    await bot.set_my_commands(commands)


async def main():
    token = os.getenv('TELEGRAM_TOKEN')
    bot = Bot(token=token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    Bot.set_current(bot)

    register_handlers(dp)

    await set_commands_helper(bot)
    await dp.skip_updates()

    await asyncio.gather(dp.start_polling(), schedule_main())


if __name__ == '__main__':
    asyncio.run(main())
