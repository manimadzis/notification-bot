from aiogram.dispatcher.filters.state import State, StatesGroup


class TimerFSM(StatesGroup):
    input_time = State()
    input_message = State()


class RepeaterFSM(StatesGroup):
    input_time = State()
    input_message = State()
