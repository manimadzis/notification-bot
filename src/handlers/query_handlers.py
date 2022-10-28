import uuid
from loguru import logger
from aiogram import types
from .import notification_store, messages


async def stop_notification_handler(query: types.CallbackQuery):
    logger.info(f"Callback query | data: {query.data}")
    uuid_key = uuid.UUID(query.data)
    user_id = query.from_user.id

    await notification_store.kill(user_id, uuid_key)

    await query.bot.send_message(query.from_user.id, messages.CANCELED)
    await query.answer()