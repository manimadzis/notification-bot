import asyncio

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

import config
import log
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
        BotCommand("/list", "список уведомлений"),
        BotCommand("/help", "помощь")
    ]
    await bot.set_my_commands(commands)


async def main():
    config.load("config.yaml")
    log.init()

    bot = Bot(token=config.config.telegram_token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    Bot.set_current(bot)
    register_handlers(dp)

    logger = log.logger

    logger.info("Setting command helper")
    await set_commands_helper(bot)

    logger.info("Skipping updates")
    await dp.skip_updates()

    logger.info("Starting telegram bot")
    await asyncio.gather(dp.start_polling(), schedule_main())


if __name__ == '__main__':
    asyncio.run(main())
