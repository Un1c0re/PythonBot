from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

button2 = KeyboardButton('желаемое')
button3 = KeyboardButton('поиск товара')
button4 = KeyboardButton('меню')
button5 = KeyboardButton('все товары')

b1 = InlineKeyboardButton('Для мужчин', callback_data='мужское')
b2 = InlineKeyboardButton('Для женщин', callback_data='женское')
b3 = InlineKeyboardButton('Для детей', callback_data='детское')
b4 = InlineKeyboardButton('Обувь', callback_data='обувь')
b5 = InlineKeyboardButton('Другое', callback_data='другое')


category_kb = InlineKeyboardMarkup(resize_keyboard=True)
category_kb.add(b1).add(b2).add(b3).add(b4).add(b5)

client_kb = ReplyKeyboardMarkup(resize_keyboard=True)
client_kb.row(button2, button3, button4).add(button5)
