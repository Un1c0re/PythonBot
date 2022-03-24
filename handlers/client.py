from aiogram import types, Dispatcher
from aiogram.types import ContentType
from aiogram.types import ShippingOption, ShippingQuery, LabeledPrice, PreCheckoutQuery

from config import PAYMENTS_PROVIDER_TOKEN
from create_bot import dp, bot
from database import sqlite_db
from keyboards import client_kb, category_kb


CATEGORIES = [
    'мужское',
    'женское',
    'детское',
    'обувь',
    'другое'
]

FAST_SHIPPING_OPTION = ShippingOption(id='fast', title='Быстрая доставка')\
    .add(LabeledPrice('Быстрая доставка', 15000))

STANDARD_SHIPPING_OPTION = ShippingOption(id='standard', title='Почта России')\
    .add(LabeledPrice('Почта России', 10000))

PICKUP_SHIPPING_OPTION = ShippingOption(id='pickup', title='Самовывоз')\
    .add(LabeledPrice('Самовывоз', 10000))


########################################################################################################################


async def command_start(message: types.Message):
    await message.answer('Добро пожаловать!', reply_markup=client_kb)
    await categories(message)


async def categories(message: types.Message):
    await message.answer('Выберите категорию', reply_markup=category_kb)


async def goto_category(callback_query: types.CallbackQuery):
    await category_products(callback_query)
    await bot.answer_callback_query(callback_query.id)


async def category_products(callback_query: types.CallbackQuery):
    list_of_products = await sqlite_db.sql_find_by_category(callback_query)
    if len(list_of_products) == 0:
        await callback_query.answer('в этой категории товаров нет')
    else:
        for product in list_of_products:
            await buy_process(callback_query.from_user.id, product)


async def all_products(message: types.Message):
    list_of_products = await sqlite_db.sql_read_every()
    for product in list_of_products:
        await buy_process(message.from_user.id, product)


async def search(message: types.Message):
    await message.answer('Введите название товара')

    @dp.message_handler()
    async def find(msg: types.Message):
        product = await sqlite_db.sql_find_command(msg)
        await buy_process(message.from_user.id, product)


async def buy_process(from_user_id, product):
    prices = [LabeledPrice(label=f'вы покупаете {product[1]}', amount=int(f'{product[-1]}') * 100)]
    await bot.send_invoice(
        from_user_id,
        title=f'Товар: {product[1]}',
        description=f'Категория: {product[2]}',
        photo_url=product[0],
        photo_height=512,
        photo_width=512,
        photo_size=512,
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        need_phone_number=False,
        need_email=False,
        is_flexible=True,
        prices=prices,
        start_parameter='example',
        payload='some_invoice',
    )


async def shipping_process(shipping_query: ShippingQuery):
    if shipping_query.shipping_address.country_code == 'AU':
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message='Доставка в выбранном регионе недоступна.'
        )

    shipping_options_list = [FAST_SHIPPING_OPTION]

    if shipping_query.shipping_address.country_code == 'RU':
        shipping_options_list.append(STANDARD_SHIPPING_OPTION)

        if shipping_query.shipping_address.city == 'Сургут':
            shipping_options_list.append(PICKUP_SHIPPING_OPTION)

    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=shipping_options_list
    )


async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def successful_payment(message: types.Message):
    total_amount = message.successful_payment.total_amount // 100
    currency = message.successful_payment.currency
    await bot.send_message(
        message.from_user.id,
        f'Покупка успешно совершена. Итоговая сумма составила {total_amount} {currency}'
    )


########################################################################################################################


def register_handlers_client(dispatcher: Dispatcher):

    dispatcher.register_message_handler(command_start, commands=['start', 'help'])

    dispatcher.register_message_handler(categories, lambda message: 'меню' in message.text)

    dispatcher.register_callback_query_handler(goto_category, lambda query: query.data in CATEGORIES)

    dispatcher.register_message_handler(all_products, lambda message: 'все товары' in message.text)

    dispatcher.register_message_handler(search, lambda message: 'поиск товара' in message.text)

    dispatcher.register_shipping_query_handler(shipping_process, lambda q: True)

    dispatcher.register_pre_checkout_query_handler(checkout_process, lambda q: True)

    dispatcher.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
