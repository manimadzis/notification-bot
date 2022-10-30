import uuid

import aiogram

import notification_store
import schedule
from log import logger
from src import messages, utils, keyboards, fsm
from src.notification import Repeater, Timer, Notification


class Bot:
    def __init__(self,
                 token: str,
                 scheduler: schedule.Scheduler,
                 aiogram_storage: aiogram.dispatcher.storage.BaseStorage,
                 store: notification_store.NotificationStoreBase
                 ):
        self._bot = aiogram.Bot(token=token)
        self._dp = aiogram.Dispatcher(self._bot, storage=aiogram_storage)

        self._logger = logger
        self._scheduler = scheduler
        self._store = store

        # self._dp.register_message_handler(self._start_handler, commands=["start"], state="*")


        # self._register_handlers()

    async def _set_command_list(self):
        commands = [aiogram.types.BotCommand("/start", "начать работу с ботом, вернуться в меню"),
                    aiogram.types.BotCommand("/timer", "запустить таймер"),
                    aiogram.types.BotCommand("/repeater", "запустить повторитель"),
                    aiogram.types.BotCommand("/stop", "остановить"),
                    aiogram.types.BotCommand("/list", "список уведомлений"),
                    aiogram.types.BotCommand("/help", "помощь")]

        await self._bot.set_my_commands(commands)

    def _register_handlers(self):
        self._register_commands()
        self._register_timer_handlers()
        self._register_repeater_handlers()
        self._register_queries()

    def _register_timer_handlers(self):
        self._dp.register_message_handler(self._timer_fsm_command_handler, lambda msg: msg.text == keyboards.TIMER)
        self._dp.register_message_handler(self._timer_fsm_input_time_handler, state=fsm.TimerFSM.input_time)
        self._dp.register_message_handler(self._timer_fsm_input_message_handler, state=fsm.TimerFSM.input_message)

    def _register_repeater_handlers(self):
        self._dp.register_message_handler(self._repeater_fsm_command_handler,
                                          lambda msg: msg.text == keyboards.REPEAT_TIMER)
        self._dp.register_message_handler(self._repeater_fsm_input_time_handler, state=fsm.RepeaterFSM.input_time)
        self._dp.register_message_handler(self._repeater_fsm_input_message_handler,
                                          state=fsm.RepeaterFSM.input_message)

    def _register_commands(self):
        self._dp.register_message_handler(self._start_handler, commands=["start"], state="*")
        self._dp.register_message_handler(self._help_handler, commands=["help"], state="*")
        self._dp.register_message_handler(self._stop_handler, commands=["stop"], state="*")
        self._dp.register_message_handler(self._timer_handler, commands=["timer"], state="*")
        self._dp.register_message_handler(self._repeater_handler, commands=["repeater"], state="*")
        self._dp.register_message_handler(self._list_handler, commands=["list"], state="*")

    def _register_queries(self):
        self._dp.register_callback_query_handler(self._query_stop_notification_handler)

    # COMMAND HANDLERS

    async def _start_handler(self, msg: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
        logger.trace(f"Handle /start: {msg}")

        await self._help_handler(msg)
        await state.reset_state()

    @staticmethod
    async def _help_handler(msg: aiogram.types.Message):
        logger.trace(f"Handle /help: {msg}")

        await msg.answer(messages.HELP_MSG, reply_markup=keyboards.start_keyboard)

    async def _stop_handler(self, msg: aiogram.types.Message):
        logger.trace(f"Handle /stop: {msg}")

        user_notifications = await self._store.get_by_chat_id(msg.chat.id)
        message = self._notification_list(msg.chat.id)
        markup = aiogram.types.InlineKeyboardMarkup()

        for i, uuid_key in enumerate(user_notifications, start=1):
            markup.add(aiogram.types.InlineKeyboardButton(str(i), callback_data=str(uuid_key)))

        await msg.answer(message, reply_markup=markup)

    @staticmethod
    async def _timer_handler(msg: aiogram.types.Message):
        logger.trace(f"Handle /timer: {msg}")

        split = msg.text.split(maxsplit=1)
        if len(split) != 2:
            logger.info(messages.EMPTY_TIME)
            await msg.answer(messages.EMPTY_TIME)
            return

        period = utils.parse_duration(split[1])

        if not period:
            logger.info(messages.INVALID_TIME)
            await msg.answer(messages.INVALID_TIME)
            return

        timer = Timer(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
        await timer.run()

        await msg.answer(messages.TIMER_SET)

    @staticmethod
    async def _repeater_handler(msg: aiogram.types.Message):
        logger.trace(f"Handle /repeater: {msg}")

        split = msg.text.split(maxsplit=1)
        if len(split) != 2:
            logger.info(messages.EMPTY_TIME)
            await msg.answer(messages.EMPTY_TIME)

        period = utils.parse_duration(split[1])

        if not period:
            logger.info(messages.INVALID_TIME)
            await msg.answer(messages.INVALID_TIME)
            return

        repeater = Repeater(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message="Hi")
        await repeater.run()

        await msg.answer(messages.REPEATER_SET)

    async def _notification_list(self, chat_id: int) -> str:
        user_notifications = await self._store.get_by_chat_id(chat_id)
        if len(user_notifications) == 0:
            return messages.NO_NOTIFICATIONS

        message = messages.YOURS_NOTIFICATIONS + ":\n"
        for i, notification in enumerate(user_notifications, start=1):
            message += f"{i}. {messages.MESSAGE}: {user_notifications[notification.uuid_key].message}\n    {user_notifications[notification.uuid_key].before()}\n"

        return message

    async def _list_handler(self, msg: aiogram.types.Message):
        logger.trace(f"Handle /list: {msg}")
        await msg.answer(await self._notification_list(msg.chat.id))

    # TIMER FMS HANDLERS

    async def _timer_fsm_command_handler(self, msg: aiogram.types.Message):
        logger.trace(f"Handle Timer: {msg}")
        await msg.answer(messages.INPUT_TIME, reply_markup=keyboards.timer_keyboard)
        await fsm.TimerFSM.input_time.set()

    async def _timer_fsm_input_time_handler(self, msg: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
        logger.trace(f"Handle Timer input time: {msg}")
        period = utils.parse_duration(msg.text)
        if period:
            await fsm.TimerFSM.input_message.set()
            await state.update_data({"period": period})
            await msg.answer(messages.INPUT_MESSAGE, reply_markup=keyboards.notify_message_keyboard)
        else:
            await msg.answer(messages.INVALID_TIME)

    async def _timer_fsm_input_message_handler(self, msg: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
        logger.trace(f"Handle Timer input time: {msg}")
        if msg.text == keyboards.BY_DEFAULT:
            message = messages.MESSAGE_BY_DEFAULT
        else:
            message = msg.text

        period = (await state.get_data())["period"]

        timer = Timer(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message=message)
        await timer.run()
        await self._store.add(timer)
        await state.finish()

        await msg.answer(messages.TIMER_SET, reply_markup=keyboards.start_keyboard)
        logger.info("Set timer")

    # QUERY HANDLERS

    async def _query_stop_notification_handler(self, query: aiogram.types.CallbackQuery):
        logger.info(f"Callback query | data: {query.data}")

        try:
            uuid_key = uuid.UUID(query.data)
        except ValueError as e:
            logger.exception(e)
            return

        user_id = query.from_user.id
        notification = Notification(chat_id=user_id, uuid_key=uuid_key)
        await self._store.kill(notification)

        await query.bot.send_message(query.from_user.id, messages.CANCELED)
        await query.answer()

    # REPEATER HANDLERS

    async def _repeater_fsm_command_handler(self, msg: aiogram.types.Message):
        await msg.answer(messages.INPUT_TIME, reply_markup=keyboards.timer_keyboard)
        await fsm.RepeaterFSM.input_time.set()

    async def _repeater_fsm_input_time_handler(self, msg: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
        period = utils.parse_duration(msg.text)
        if period:
            await fsm.RepeaterFSM.input_message.set()
            await state.update_data({"period": period})
            await msg.answer(messages.INPUT_MESSAGE, reply_markup=keyboards.notify_message_keyboard)
        else:
            await msg.answer(messages.INVALID_TIME)

    async def _repeater_fsm_input_message_handler(self, msg: aiogram.types.Message,
                                                  state: aiogram.dispatcher.FSMContext):
        if msg.text == keyboards.BY_DEFAULT:
            message = messages.MESSAGE_BY_DEFAULT
        else:
            message = msg.text

        period = (await state.get_data())["period"]

        repeater = Repeater(send_func=msg.bot.send_message, chat_id=msg.chat.id, period=period, message=message)
        await repeater.run()
        await state.finish()

        await msg.answer(messages.REPEATER_SET, reply_markup=keyboards.start_keyboard)
        logger.info(messages.REPEATER_SET)

    async def start(self):
        logger.info("Setting command list")
        await self._set_command_list()
        logger.info("Skipping updates")
        await self._dp.skip_updates()
        logger.info("Starting telegram bot")
        await self._dp.start_polling()
