import datetime

from aiogram import types

import inline_keyboards
import keyboards
import utils
from init import *


@dp.callback_query_handler(lambda callback_query: callback_query.data == inline_keyboards.TIMER)
async def handler(callback_query: types.CallbackQuery):
    await callback_query.answer("", False, cache_time=5)


@dp.callback_query_handler(lambda callback_query: callback_query.data == inline_keyboards.REPEAT_TIMER)
async def handler(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Set repeat timer")
    await callback_query.answer("", False, cache_time=0)


@dp.callback_query_handler(lambda callback_query: callback_query.data == inline_keyboards.ALARM)
async def handler(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Set alarm")
    await callback_query.answer("", False, cache_time=0)
