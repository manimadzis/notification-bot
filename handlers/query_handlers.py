import uuid

from aiogram import types

from handlers.notifications import notifications


async def stop_notification_handler(callback_query: types.CallbackQuery):
    uuid_key = uuid.UUID(callback_query.data)
    user_id = callback_query.from_user.id
    await notifications[user_id][uuid_key].stop()
    await callback_query.bot.send_message(callback_query.from_user.id, "Отменено")
    await callback_query.answer()
    del notifications[user_id][uuid_key]
