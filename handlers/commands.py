from aiogram import types
from aiogram.dispatcher import FSMContext
from loguru import logger

import keyboards
from handlers import notifications
from handlers.messages import *
from handlers.notifications import Timer, Repeater
from handlers.parser import parse_duration


async def start_handler(msg: types.Message, state: FSMContext):
    await help_handler(msg)
    await state.reset_state()


async def help_handler(msg: types.Message):
    await msg.answer(HELP_MSG, reply_markup=keyboards.start_keyboard)


async def stop_handler(msg: types.Message):
    user_notifications = notifications.get(msg.chat.id)
    message = notification_list(msg.chat.id)
    markup = types.InlineKeyboardMarkup()

    for i, uuid_key in enumerate(user_notifications, start=1):
        markup.add(types.InlineKeyboardButton(str(i), callback_data=str(uuid_key)))

    await msg.answer(message, reply_markup=markup)


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

    await msg.answer(REPEATER_SET)


def notification_list(chat_id: int) -> str:
    user_notifications = notifications.get(chat_id)
    if len(user_notifications) == 0:
        return NO_NOTIFICATIONS

    message = YOURS_NOTIFICATIONS + ":\n"
    for i, uuid_key in enumerate(user_notifications, start=1):
        message += f"{i}. {MESSAGE}: {user_notifications[uuid_key].message}\n    {user_notifications[uuid_key].before()}\n"

    return message


async def list_handler(msg: types.Message):
    await msg.answer(notification_list(msg.chat.id))
