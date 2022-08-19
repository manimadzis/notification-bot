import sys

from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

import keyboards
from handlers.notifications import notifications
from handlers.parser import parse_duration
from schedule import Timer, Repeater

HELP_MSG = """Бот-уведомитель
/start - начать работу с ботом, вернуться в меню
/timer <время> - запустить таймер
/repeater <время> - запустить повторитель
/stop - остановить
/help - вызвать это сообщение
"""

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


async def start_handler(msg: types.Message, state: FSMContext):
    await help_handler(msg)
    await state.reset_state()


async def help_handler(msg: types.Message):
    await msg.answer(HELP_MSG, reply_markup=keyboards.start_keyboard)


async def stop_handler(msg: types.Message):
    for notification in notifications[msg.chat.id]:
        await notification.stop()
    del notifications[msg.chat.id]

    await msg.answer("Остановлено")


async def stop2_handler(msg: types.Message):
    user_notifications = notifications[msg.chat.id]
    if len(user_notifications) == 0:
        await  msg.answer("Нет напоминанний")
        logger.info(f"{msg.chat.id}: Нет напоминанний")
    else:
        markup = types.InlineKeyboardMarkup()
        for user_notification in user_notifications:
            markup.add(types.InlineKeyboardButton(str(user_notification), callback_data="3"))
        await msg.answer("Ваши напоминания", reply_markup=markup)


async def timer_handler(msg: types.Message):
    splitted = msg.text.split(maxsplit=1)
    if len(splitted) != 2:
        logger.info("Не указано время")
        await msg.answer("Не указано время")

    period = parse_duration(splitted[1])

    if not period:
        logger.info("Невалидный формат времени")
        await msg.answer("Невалидный формат времени")
        return

    timer = Timer(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
    await timer.run()

    notifications[msg.chat.id].append(timer)

    await msg.answer("Таймер установлен")


async def repeater_handler(msg: types.Message):
    splitted = msg.text.split(maxsplit=1)
    if len(splitted) != 2:
        logger.info("Не указано время")
        await msg.answer("Не указано время")

    period = parse_duration(splitted[1])

    if not period:
        logger.info("Невалидный формат времени")
        await msg.answer("Невалидный формат времени")
        return

    repeater = Repeater(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
    await repeater.run()

    notifications[msg.chat.id].append(repeater)

    await msg.answer("Повторитель установлен")
