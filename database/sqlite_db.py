import sqlite3 as sq

from create_bot import dp, bot


def sql_start():
    global base, cursor
    base = sq.connect('store.db')
    cursor = base.cursor()
    if base:
        print('Data base connected successfully!')

    base.execute('CREATE TABLE IF NOT EXISTS products(img TEXT, name TEXT, category TEXT, price TEXT)')
    base.commit()


async def sql_add_to_products(state):
    async with state.proxy() as data:
        cursor.execute('INSERT INTO products VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read_every():
    return cursor.execute('SELECT * FROM products').fetchall()


async def sql_find_by_category(callback_query):
    return cursor.execute('SELECT * FROM products WHERE category == ?', (callback_query.data,)).fetchall()


async def sql_delete_command(data):
    cursor.execute('DELETE FROM products WHERE name == ?', (data,))
    base.commit()


async def sql_find_command(message):
    products_list = cursor.execute('SELECT * FROM products WHERE name == ?', (message.text.lower(),)).fetchall()
    for product in products_list:
        return product
