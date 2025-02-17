import datetime
from random import choice, randint

from aiogram import types
from aiogram.dispatcher import filters

from commands.truth_or_dare import get_wish
from configuration import *
from database.DatabseManager import DatabaseManager
from loader import dp, bot

last_time_horo = datetime.datetime.now() - datetime.timedelta(days=1)


@dp.message_handler(commands=['horo_for_all'])
async def solo_horo(message: types.Message):
    global last_time_horo
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name,
                              message.from_user.last_name)
        users = db_worker.get_users(message.chat.id)
    now_time = datetime.datetime.now()
    delta = now_time - last_time_horo
    out = ''
    if delta.seconds > wait_seconds_for_horo or delta.days > 0:
        last_time_horo = now_time
        for user_id, name, surname in users:
            today_horo = get_wish(users)
            out += f'[{name}](tg://user?id={user_id}){today_horo}\n'
        await bot.send_message(message.chat.id, out, parse_mode='Markdown', reply_to_message_id=message.message_id)
    else:
        await bot.send_message(message.chat.id,
                               f'До использования команды заново осталось {(wait_seconds_for_horo - delta.seconds) // 3600} часов')
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(filters.Text(equals='!Гороскоп', ignore_case=True))
@dp.message_handler(commands=['horo'])
async def all_horo(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name,
                              message.from_user.last_name)
        today_horo = get_wish(db_worker.get_users(message.chat.id))
    out = f'{message.from_user.first_name}{"" if message.from_user.last_name is None else " " + str(message.from_user.last_name)}{today_horo}'
    await bot.send_message(message.chat.id, out, reply_to_message_id=message.message_id)

