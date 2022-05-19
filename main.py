from aiogram.utils.executor import start_webhook
from aiogram import executor
from handlers import *
from create_bot import *
from database import sqlite_db


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start
    client.register_handlers_client(dp)
    print('Bot is online')
    sqlite_db.sql_start()

    admin.register_handlers_client(dp)
    client.register_handlers_client(dp)


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    # await dp.storage.close()
    # await dp.storage.wait_closed()

    logging.warning('Bye!')

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
