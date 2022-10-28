from aiogram.dispatcher.dispatcher import Dispatcher

from . import query_handlers, timer_fsm, commands, repeater_fsm, keyboards


def register_handlers(dp: Dispatcher):
    register_commands(dp)
    register_timer_handlers(dp)
    register_repeater_handlers(dp)
    register_queries(dp)


def register_timer_handlers(dp: Dispatcher):
    dp.register_message_handler(timer_fsm.command_handler, lambda msg: msg.text == keyboards.TIMER)
    dp.register_message_handler(timer_fsm.input_time_handler, state=timer_fsm.TimerFSM.input_time)
    dp.register_message_handler(timer_fsm.input_message_handler, state=timer_fsm.TimerFSM.input_message)


def register_repeater_handlers(dp: Dispatcher):
    dp.register_message_handler(repeater_fsm.command_handler, lambda msg: msg.text == keyboards.REPEAT_TIMER)
    dp.register_message_handler(repeater_fsm.input_time_handler, state=repeater_fsm.RepeaterFSM.input_time)
    dp.register_message_handler(repeater_fsm.input_message_handler, state=repeater_fsm.RepeaterFSM.input_message)


def register_commands(dp: Dispatcher):
    dp.register_message_handler(commands.start_handler, commands=["start"], state="*")
    dp.register_message_handler(commands.help_handler, commands=["help"], state="*")
    dp.register_message_handler(commands.stop_handler, commands=["stop"], state="*")
    dp.register_message_handler(commands.timer_handler, commands=["timer"], state="*")
    dp.register_message_handler(commands.repeater_handler, commands=["repeater"], state="*")
    dp.register_message_handler(commands.list_handler, commands=["list"], state="*")


def register_queries(dp: Dispatcher):
    dp.register_callback_query_handler(query_handlers.stop_notification_handler)