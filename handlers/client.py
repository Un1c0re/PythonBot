from aiogram import types, Dispatcher
from aiogram.types import LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup, ContentType

from create_bot import dp, bot
from keyboards import client_kb, category_kb
from database import sqlite_db

from config import PAYMENTS_PROVIDER_TOKEN


categories_list = [
    'мужское',
    'женское',
    'детское',
    'обувь',
    'другое'
]


async def buy_message(from_user_id, product):
    prices = [LabeledPrice(label=f'вы покупаете {product[1]}', amount=int(f'{product[-1]}') * 100)]

    await bot.send_invoice(
        from_user_id,
        title=f'Товар: {product[1]}',
        description=f'Категория: {product[2]}',
        # photo_url='https://dubna.ru/sites/default/files/articles/2021/08/24/13769.jpg',
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        need_phone_number=False,
        need_email=False,
        is_flexible=False,
        prices=prices,
        start_parameter='start_parameter',
        payload='coupon',
        reply_markup=(InlineKeyboardMarkup(resize_keyboard=True).row(
            InlineKeyboardButton('купить сейчас', pay=True),
            InlineKeyboardButton('в желаемое', callback_data='to_desires')))
    )


async def category_products(callback_query: types.CallbackQuery):
    list_of_products = await sqlite_db.sql_find_by_category(callback_query)
    for product in list_of_products:
        await bot.send_photo(callback_query.from_user.id,
                             product[0], f'{product[1]}\nКатегория: {product[2]}\nЦена: {product[-1]}')
        await buy_message(callback_query.from_user.id, product)


###########################################################################################################


async def command_start(message: types.Message):
    await message.answer('Добро пожаловать!', reply_markup=client_kb)
    await categories(message)


async def categories(message: types.Message):
    await message.answer('Выберите категорию', reply_markup=category_kb)


async def goto_category(callback_query: types.CallbackQuery):
    await category_products(callback_query)
    await bot.answer_callback_query(callback_query.id)


async def all_products(message: types.Message):
    list_of_products = await sqlite_db.sql_read_every()
    for product in list_of_products:
        await bot.send_photo(message.from_user.id,
                             product[0], f'{product[1]}\nКатегория: {product[2]}\nЦена: {product[-1]}')
        await buy_message(message.from_user.id, product)


async def search(message: types.Message):
    await message.answer('Введите название товара')

    @dp.message_handler()
    async def find(msg: types.Message):
        product = await sqlite_db.sql_find_command(msg)
        await buy_message(message.from_user.id, product)


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    payment = message.successful_payment.to_python()
    for key, val in payment.items():
        print(f'{key} = {val}')

    await message.answer(
        'successful_payment'.format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency
        )
    )


# @dp.callback_query_handler(lambda query: query.data == 'to_desires')
# async def add_to_desires(callback_query: types.CallbackQuery):
#     pass


async def desires(message: types.Message):
    await message.answer('Ваш список желаемого пуст')


def register_handlers_client(dispatcher: Dispatcher):

    dispatcher.register_message_handler(command_start, commands=['start', 'help'])

    dispatcher.register_message_handler(categories, lambda message: 'меню' in message.text)

    dispatcher.register_callback_query_handler(goto_category, lambda query: query.data in categories_list)

    dispatcher.register_message_handler(all_products, lambda message: 'все товары' in message.text)

    dispatcher.register_message_handler(search, lambda message: 'поиск товара' in message.text)

    dispatcher.register_message_handler(desires, lambda message: 'желаемое' in message.text)
