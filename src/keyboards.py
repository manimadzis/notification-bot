from aiogram import types

time_intervals = {
    "10 s": 10,
    "10 m": 10,
    "30 m": 10,
}

TIMER = "Timer"
REPEAT_TIMER = "Repeater"
BY_DEFAULT = "По умолчанию"

timer_keyboard = types.ReplyKeyboardMarkup(
    [[types.KeyboardButton("10 s"), types.KeyboardButton("10 m")],
     [types.KeyboardButton("30 m")]]
)

start_keyboard = types.ReplyKeyboardMarkup(
    [
        [types.KeyboardButton(TIMER), types.KeyboardButton(REPEAT_TIMER)],
    ]
)


notify_message_keyboard = types.ReplyKeyboardMarkup(
    [
        [types.KeyboardButton(BY_DEFAULT)]
    ]
)