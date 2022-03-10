import sqlite3 as sq

from create_bot import dp, bot


def sql_start():
    global base, cur
    base = sq.connect('store.db')
    cur = base.cursor()
    if base:
        print('Data base connected successfully!')

    base.execute('CREATE TABLE IF NOT EXISTS products(img TEXT, name TEXT, category TEXT, price TEXT)')
    # base.execute('CREATE TABLE IF NOT EXISTS desires(img TEXT, name TEXT, category TEXT, price TEXT)')
    base.commit()


async def sql_add_to_products(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO products VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


# async def sql_add_to_desires():
#     cur.execute('INSERT INTO desires VALUES (?, ?, ?, ?)', )


async def sql_read_every():
    return cur.execute('SELECT * FROM products').fetchall()


async def sql_find_by_category(callback_query):
    return cur.execute('SELECT * FROM products WHERE category == ?', (callback_query.data,)).fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM products WHERE name == ?', (data,))
    base.commit()


async def sql_find_command(message):
    products_list = cur.execute('SELECT * FROM products WHERE name == ?', (message.text.lower(),)).fetchall()
    for product in products_list:
        await bot.send_photo(message.from_user.id, product[0],
                             f'{product[1]}\nКатегория: {product[2]}\nЦена: {product[-1]}')
        return product

