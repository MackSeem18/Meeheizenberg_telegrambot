import telebot
import sqlite3

with open('data/TOKEN_test.txt') as t:
    TOKEN = t.read()


bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=['start'])
def start(message):
    db = sqlite3.connect('users_data.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS chat_data(
        chat_id INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS beer_info(
        chat_id INTEGER,
        place TEXT,
        date TEXT,
        time TEXT
    )""")

    db.commit()

    cursor.execute(f"SELECT chat_id FROM chat_data WHERE chat_id = {message.chat.id}")
    data = cursor.fetchone()
    if data is None:
        cursor.execute("INSERT INTO chat_data VALUES(?);", [message.chat.id])
        cursor.execute("INSERT INTO beer_info VALUES(?, ?, ? ,?);", [message.chat.id, "", "", ""])
        db.commit()
        bot.send_message(message.chat.id, "Привет, я бот организатор. Помогу запланировать встречи и всё что с ними связано, чтобы узнать список команд напиши /help")
    else:
        bot.send_message(message.chat.id, "Привет ещё раз! Чтобы вспомнить список команд используй /help")

    db.close()


@bot.message_handler(commands=['help'])
def commands(message):
    with open('data/Commands.txt') as h:
        commands_list = h.read()
    bot.send_message(message.chat.id, commands_list)


@bot.message_handler(commands=['delete_beer'])
def delete_beer(message):
    bot.send_message(message.chat.id, 'Ты уверен, что хочешь удалить запись о следующей встрече? Ответь на это сообщение "Да" для удаления и "Нет", чтобы оставить всё как есть.')
    bot.register_next_step_handler(message, delete_beer_from_db)


def delete_beer_from_db(message):
    if message.text.lower() == 'да':
        db = sqlite3.connect('users_data.db')
        cursor = db.cursor()

        cursor.execute(f"SELECT place, date, time FROM beer_info WHERE chat_id = {message.chat.id}")
        data = cursor.fetchall()
        place, date, time = data[0][0], data[0][1], data[0][2]
        if place == '' or date == '' or time == '':
            bot.reply_to(message, "Следующая встреча ещё не назначена, мне нечего удалять. Назначь встречу с помощью /beer")
        else:
            cursor.execute(
                f"UPDATE beer_info SET place='', date='', time='' WHERE chat_id = {message.chat.id}")
            db.commit()
            bot.send_message(message.chat.id, f'Информация о встрече удалена.')

        db.close()
    elif message.text.lower() == 'нет':
        bot.reply_to(message, "Понял, ничего не удаляю. Чтобы узнать где и когда следующая встреча используй /next")
    else:
        bot.reply_to(message, 'Извини я ничего не понял. Напиши в ответ "Да", чтобы удалить информацию о встрече и "Нет", чтобы ничего не удалять.')
        bot.register_next_step_handler(message, delete_beer_from_db)


@bot.message_handler(commands=['next'])
def get_next_beer_info(message):
    db = sqlite3.connect('users_data.db')
    cursor = db.cursor()

    cursor.execute(f"SELECT place, date, time FROM beer_info WHERE chat_id = {message.chat.id}")
    data = cursor.fetchall()
    place, date, time = data[0][0], data[0][1], data[0][2]
    if place == '' or date == '' or time == '':
        bot.reply_to(message, "Следующая встреча ещё не назначена. Назначь встречу с помощью /beer")
    else:
        bot.send_message(message.chat.id, f'Следующая встреча состоится в {place}, {date} в {time}')

    db.close()


def add_next_beer(place, date, time, message):
    db = sqlite3.connect('users_data.db')
    cursor = db.cursor()

    cursor.execute(f"UPDATE beer_info SET place='{place}', date='{date}', time='{time}' WHERE chat_id = {message.chat.id}")
    db.commit()

    bot.send_message(message.chat.id, f'Следующая встреча состоится в {place}, {date} в {time}')

    db.close()


@bot.message_handler(commands=['beer'])
def register_meeting(message):
    bot.reply_to(message, 'Записываю новую встречу. Ответь на это сообщение в формате "МЕСТО, ДАТА, ВРЕМЯ". Если передумаешь, напиши "Отмена", чтобы отменить запись')
    bot.register_next_step_handler(message, get_beer_data)


def get_beer_data(message):
    if message.text.lower() != "отмена":
        if message.text.count(',') == 2:
            info = message.text
            place_info, date_info, time_info = info.split(',', 2)

            if date_info.startswith(' '):
                date_info = date_info[1:]
            if time_info.startswith(' '):
                time_info = time_info[1:]

            add_next_beer(place_info, date_info, time_info, message)

        else:
            bot.reply_to(message, 'Извини, что-то пошло не так и я тебя не понял, давай попробуем ещё раз. Ответь мне в формате "МЕСТО, ДАТА, ВРЕМЯ". Используй запятую в качестве разделителя. Если передумаешь, напиши "Отмена"')
            bot.register_next_step_handler(message, get_beer_data)

    else:
        bot.reply_to(message, 'Отменяю запись. Чтобы узнать, где и когда следующая встреча используй /next')


bot.infinity_polling()
