from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from . import keyboards, messages
from .notification_store import Repeater
from .parser import parse_duration


class RepeaterFSM(StatesGroup):
    input_time = State()
    input_message = State()


async def command_handler(msg: types.Message):
    await msg.answer(messages.INPUT_TIME, reply_markup=keyboards.timer_keyboard)
    await RepeaterFSM.input_time.set()


async def input_time_handler(msg: types.Message, state: FSMContext):
    period = parse_duration(msg.text)
    if period:
        await RepeaterFSM.input_message.set()
        await state.update_data({"period": period})
        await msg.answer(messages.INPUT_MESSAGE, reply_markup=keyboards.notify_message_keyboard)
    else:
        await msg.answer(messages.INVALID_TIME)


async def input_message_handler(msg: types.Message, state: FSMContext):
    if msg.text == keyboards.BY_DEFAULT:
        message = messages.MESSAGE_BY_DEFAULT
    else:
        message = msg.text

    period = (await state.get_data())["period"]

    repeater = Repeater(msg.bot.send_message, chat_id=msg.chat.id, period=period, message=message)
    await repeater.run()
    await state.finish()

    await msg.answer(messages.REPEATER_SET, reply_markup=keyboards.start_keyboard)
    logger.info(messages.REPEATER_SET)
