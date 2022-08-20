import sys
import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

import keyboards
from handlers.messages import *
from handlers.notifications import notifications
from handlers.parser import parse_duration
from schedule import Timer, Repeater

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


async def start_handler(msg: types.Message, state: FSMContext):
    await help_handler(msg)
    await state.reset_state()


async def help_handler(msg: types.Message):
    await msg.answer(HELP_MSG, reply_markup=keyboards.start_keyboard)


async def stop_handler(msg: types.Message):
    user_notifications = notifications[msg.chat.id]
    if len(user_notifications) == 0:
        await msg.answer(NO_NOTIFICATIONS)
        logger.info(f"{msg.chat.id}: {NO_NOTIFICATIONS}")
    else:
        markup = types.InlineKeyboardMarkup()
        for uuid_key in user_notifications:
            markup.add(types.InlineKeyboardButton(str(user_notifications[uuid_key]), callback_data=str(uuid_key)))
        await msg.answer(YOURS_NOTIFICATIONS, reply_markup=markup)


async def timer_handler(msg: types.Message):
    split = msg.text.split(maxsplit=1)
    if len(split) != 2:
        logger.info(EMPTY_TIME)
        await msg.answer(EMPTY_TIME)
        return

    period = parse_duration(split[1])

    if not period:
        logger.info(INVALID_TIME)
        await msg.answer(INVALID_TIME)
        return

    timer = Timer(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
    await timer.run()

    notifications[msg.chat.id][uuid.uuid4()] = timer

    await msg.answer(TIMER_SET)


async def repeater_handler(msg: types.Message):
    split = msg.text.split(maxsplit=1)
    if len(split) != 2:
        logger.info(EMPTY_TIME)
        await msg.answer(EMPTY_TIME)

    period = parse_duration(split[1])

    if not period:
        logger.info(INVALID_TIME)
        await msg.answer(INVALID_TIME)
        return

    repeater = Repeater(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
    await repeater.run()

    notifications[msg.chat.id][uuid.uuid4()] = repeater

    await msg.answer(REPEATER_SET)
