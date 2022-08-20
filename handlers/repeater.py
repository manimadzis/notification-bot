import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

import keyboards
from handlers.messages import *
from handlers.notifications import notifications
from handlers.parser import parse_duration
from schedule import Repeater


class RepeaterCommand(StatesGroup):
    input_time = State()
    input_message = State()


async def command_handler(msg: types.Message):
    await msg.answer(INPUT_TIME, reply_markup=keyboards.timer_keyboard)
    await RepeaterCommand.input_time.set()


async def input_time_handler(msg: types.Message, state: FSMContext):
    period = parse_duration(msg.text)
    if period:
        await RepeaterCommand.input_message.set()
        await state.update_data({"period": period})
        await msg.answer(INPUT_MESSAGE, reply_markup=keyboards.notify_message_keyboard)
    else:
        await msg.answer(INVALID_TIME)


async def input_message_handler(msg: types.Message, state: FSMContext):
    if msg.text == keyboards.BY_DEFAULT:
        message = MESSAGE_BY_DEFAULT
    else:
        message = msg.text

    period = (await state.get_data())["period"]

    repeater = Repeater(msg.bot.send_message, chat_id=msg.chat.id, period=period, message=message)
    await repeater.run()
    await state.finish()

    notifications[msg.chat.id][uuid.uuid4()] = repeater
    await msg.answer(REPEATER_SET, reply_markup=keyboards.start_keyboard)
    logger.info(REPEATER_SET)
