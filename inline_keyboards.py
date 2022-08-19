from aiogram import types

# callback data for inline buttons
TIMER = 'timer'
REPEAT_TIMER = 'repeat-timer'
ALARM = 'alarm'

timer_button = types.InlineKeyboardButton("Timer", callback_data=TIMER)
repeat_timer_button = types.InlineKeyboardButton("Repeat timer", callback_data=REPEAT_TIMER)
alarm_button = types.InlineKeyboardButton("Alarm", callback_data=ALARM)

start_markup = types.InlineKeyboardMarkup(row_width=1)
start_markup.row(timer_button)
start_markup.row(repeat_timer_button)
start_markup.row(alarm_button)

