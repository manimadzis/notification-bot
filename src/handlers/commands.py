from aiogram import types
from aiogram.dispatcher import FSMContext


from .notification_store import Timer, Repeater
from .parser import parse_duration
from . import notification_store, messages, keyboards
from src.log import logger


async def start_handler(msg: types.Message, state: FSMContext):
    logger.trace(f"Handle /start: {msg}")

    await help_handler(msg)
    await state.reset_state()


async def help_handler(msg: types.Message):
    logger.trace(f"Handle /help: {msg}")

    await msg.answer(messages.HELP_MSG, reply_markup=keyboards.start_keyboard)


async def stop_handler(msg: types.Message):
    logger.trace(f"Handle /stop: {msg}")

    user_notifications = notification_store.get(msg.chat.id)
    message = notification_list(msg.chat.id)
    markup = types.InlineKeyboardMarkup()

    for i, uuid_key in enumerate(user_notifications, start=1):
        markup.add(types.InlineKeyboardButton(str(i), callback_data=str(uuid_key)))

    await msg.answer(message, reply_markup=markup)


async def timer_handler(msg: types.Message):
    logger.trace(f"Handle /timer: {msg}")

    split = msg.text.split(maxsplit=1)
    if len(split) != 2:
        logger.info(messages.EMPTY_TIME)
        await msg.answer(messages.EMPTY_TIME)
        return

    period = parse_duration(split[1])

    if not period:
        logger.info(messages.INVALID_TIME)
        await msg.answer(messages.INVALID_TIME)
        return

    timer = Timer(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
    await timer.run()

    await msg.answer(messages.TIMER_SET)


async def repeater_handler(msg: types.Message):
    logger.trace(f"Handle /repeater: {msg}")

    split = msg.text.split(maxsplit=1)
    if len(split) != 2:
        logger.info(messages.EMPTY_TIME)
        await msg.answer(messages.EMPTY_TIME)

    period = parse_duration(split[1])

    if not period:
        logger.info(messages.INVALID_TIME)
        await msg.answer(messages.INVALID_TIME)
        return

    repeater = Repeater(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
    await repeater.run()

    await msg.answer(messages.REPEATER_SET)


def notification_list(chat_id: int) -> str:
    user_notifications = notification_store.get(chat_id)
    if len(user_notifications) == 0:
        return messages.NO_NOTIFICATIONS

    message = messages.YOURS_NOTIFICATIONS + ":\n"
    for i, uuid_key in enumerate(user_notifications, start=1):
        message += f"{i}. {messages.MESSAGE}: {user_notifications[uuid_key].message}\n    {user_notifications[uuid_key].before()}\n"

    return message


async def list_handler(msg: types.Message):
    logger.trace(f"Handle /list: {msg}")
    await msg.answer(notification_list(msg.chat.id))
