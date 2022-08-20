from aiogram.dispatcher.dispatcher import Dispatcher

import handlers.commands
import handlers.repeater
import handlers.query_handlers
import handlers.timer
import keyboards


def register_handlers(dp: Dispatcher):
    register_commands(dp)
    register_timer_handlers(dp)
    register_repeater_handlers(dp)
    register_queries(dp)


def register_timer_handlers(dp: Dispatcher):
    dp.register_message_handler(timer.command_handler, lambda msg: msg.text == keyboards.TIMER)
    dp.register_message_handler(timer.input_time_handler, state=timer.TimerCommand.input_time)
    dp.register_message_handler(timer.input_message_handler, state=timer.TimerCommand.input_message)


def register_repeater_handlers(dp: Dispatcher):
    dp.register_message_handler(repeater.command_handler, lambda msg: msg.text == keyboards.REPEAT_TIMER)
    dp.register_message_handler(repeater.input_time_handler, state=repeater.RepeaterCommand.input_time)
    dp.register_message_handler(repeater.input_message_handler, state=repeater.RepeaterCommand.input_message)


def register_commands(dp: Dispatcher):
    dp.register_message_handler(commands.start_handler, commands=["start"], state="*")
    dp.register_message_handler(commands.help_handler, commands=["help"], state="*")
    dp.register_message_handler(commands.stop_handler, commands=["stop"], state="*")
    dp.register_message_handler(commands.timer_handler, commands=["timer"], state="*")
    dp.register_message_handler(commands.repeater_handler, commands=["repeater"], state="*")
    dp.register_message_handler(commands.list_handler, commands=["list"], state="*")


def register_queries(dp: Dispatcher):
    dp.register_callback_query_handler(query_handlers.stop_notification_handler)