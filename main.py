# ТЗ
# бот - агрегатор
# функционал:
#   при выборе товара покупатель может добавить его в желаемое, купить сразу или написать продавцу
#   возможность посмотреть список желаемого
#
#   реализовать следующие команды:
#   - список желаемого
#   - документацию по работе с ботом в команде /help


from aiogram import executor
from handlers import *
from create_bot import dp
from database import sqlite_db


async def on_startup(_):
    print('Bot is online')
    sqlite_db.sql_start()

admin.register_handlers_client(dp)
client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
