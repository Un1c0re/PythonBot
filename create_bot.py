import asyncio
from aiogram import Bot, Dispatcher, types
from config import TOKEN

from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()


loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop, storage=storage)
