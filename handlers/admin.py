from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from config import ADMIN
from create_bot import bot
from database import sqlite_db
from keyboards import admin_keyboard


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    category = State()
    price = State()


async def moderator(message: types.Message):
    if message.from_user.id == ADMIN:
        await message.answer("Здравствуйте, администратор", reply_markup=admin_keyboard.button_case_admin)


async def cm_start(message: types.Message):
    if message.from_user.id == ADMIN:
        await FSMAdmin.photo.set()
        await message.answer("добавьте фото")
    else:
        await message.answer("вы не являетесь администратором")


async def cancel_handler(message: types.Message, state: FSMContext):
    await message.delete()
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer("Ввод товара отменен", reply_markup=ReplyKeyboardRemove())


async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.text
    await FSMAdmin.next()
    await message.answer("Введите название")


async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text.lower()
    await FSMAdmin.next()
    await message.answer("Добавьте категорию")


async def load_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text.lower()
    await FSMAdmin.next()
    await message.answer("Назначьте цену (меньше 10 000 000)")


async def load_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)

    await sqlite_db.sql_add_to_products(state)
    await state.finish()
    await message.answer("Товар успешно добавлен", reply_markup=ReplyKeyboardRemove())


async def delete_item(message: types.Message):
    if message.from_user.id == ADMIN:
        collection = await sqlite_db.sql_read_every()
        for item in collection:
            await bot.send_photo(message.from_user.id, item[0], f'{item[1]}\nОписание: {item[2]}\nЦена: {item[-1]}',
                                 reply_markup=InlineKeyboardMarkup()\
                                 .add(InlineKeyboardButton(f'удалить {item[1]}', callback_data=f'del {item[1]}')))


async def del_callback_item(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалено')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(moderator, commands=['admin'])

    dp.register_message_handler(cm_start, lambda message: 'добавить товар' in message.text, state=None)

    dp.register_message_handler(cancel_handler, lambda message: 'отмена' in message.text, state="*")

    dp.register_message_handler(load_photo, state=FSMAdmin.photo)

    dp.register_message_handler(load_name, state=FSMAdmin.name)

    dp.register_message_handler(load_category, state=FSMAdmin.category)

    dp.register_message_handler(load_price, state=FSMAdmin.price)

    dp.register_message_handler(delete_item, lambda message: 'удалить товар' in message.text)

    dp.register_callback_query_handler(del_callback_item, lambda x: x.data and x.data.startswith('del '))
