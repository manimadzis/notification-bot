from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import keyboards
from handlers.parser import parse_duration
from schedule import Repeater
from handlers.notifications import notifications

class RepeaterCommand(StatesGroup):
    input_time = State()
    input_message = State()


async def command_handler(msg: types.Message):
    await msg.answer("Введите время: ", reply_markup=keyboards.timer_keyboard)
    await RepeaterCommand.input_time.set()


async def input_time_handler(msg: types.Message, state: FSMContext):
    period = parse_duration(msg.text)
    if period:
        await RepeaterCommand.input_message.set()
        await state.update_data({"period": period})
        await msg.answer("Введите сообщение: ", reply_markup=keyboards.notify_message_keyboard)
    else:
        await msg.answer("Невалидное время")


async def input_message_handler(msg: types.Message, state: FSMContext):
    if msg.text == keyboards.BY_DEFAULT:
        message = "Hi"
    else:
        message = msg.text

    period = (await state.get_data())["period"]

    repeater = Repeater(msg.bot.send_message, chat_id=msg.chat.id, period=period, message=message)
    await repeater.run()
    await state.finish()

    notifications[msg.chat.id].append(repeater)
    await msg.answer("Повторитель установлен", reply_markup=keyboards.start_keyboard)
