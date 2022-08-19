from aiogram import types
from handlers.notifications import  notifications


async def stop_notification_handler(callback_query: types.CallbackQuery):
    index = int(callback_query.data)
    await notifications[callback_query.from_user.id][index].stop()
    await callback_query.bot.send_message(callback_query.from_user.id, "Отменено")
    await callback_query.answer()

