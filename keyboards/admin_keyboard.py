from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


button_load = KeyboardButton("добавить товар")
button_delete = KeyboardButton("удалить товар")
button_cancel = KeyboardButton("отмена")

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True)
button_case_admin.row(button_load, button_delete, button_cancel)
