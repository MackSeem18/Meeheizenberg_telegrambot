import telebot

bot = telebot.TeleBot("", parse_mode=None)
place = ''
time = ''

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет, я бот организатор. Помогу запланировать встречи и всё что с ними связано, чтобы узнать список команд напиши /help")

@bot.message_handler(commands=['help'])
def commands(message):
    bot.send_message(message.chat.id, "/start - Начало работы\n/beer - Назначить встречу \n/delete_beer - Удалить встречу \n/next - Узнать когда и где следующая встреча \n/ready_commands - Узнать список рабочих команд \n/money - Рассчитать кто сколько должен после встречи(не готово)")


@bot.message_handler(commands=['ready_commands'])
def ready_commands(message):
    bot.send_message(message.chat.id, "/start - Начало работы \n/beer - Назначить встречу \n/delete_beer - Удалить встречу \n/next - Узнать когда и где следующая встреча \n/ready_commands - Узнать список рабочих команд")


@bot.message_handler(commands=['money'])
def money(message):
    bot.send_message(message.chat.id, 'Извините, но данная функциональность ещё не реализована 😔. Вы можете узнать о доступных функциях с помощью /ready_commands')


@bot.message_handler(commands=['delete_beer'])
def delete_beer(message):
    global place
    global time
    place = ''
    time = ''
    bot.send_message(message.chat.id, 'Информация о встрече удалена')


@bot.message_handler(commands=['next'])
def next_beer(message):
    if place == '' or time == '':
        bot.reply_to(message, "Следующая встреча ещё не назначена. Назначь встречу с помощью /beer")
    else:
        bot.send_message(message.chat.id, f'Следующая встреча состоится в {place}, {time}')


@bot.message_handler(commands=['beer'])
def register_meeting(message):
    bot.reply_to(message, "Записываю следующую встречу. Напиши место встречи в ответ на это сообщение")
    bot.register_next_step_handler(message, get_place)


def get_place(message):
    global place
    place = message.text
    bot.reply_to(message, 'Записал. Напиши дату и время в ответ на это сообщение')
    bot.register_next_step_handler(message, get_time)


def get_time(message):
    global time
    time = message.text
    bot.reply_to(message, 'Записал.')
    if place == '' or time == '':
        bot.send_message(message.chat.id, f'Похоже ты что-то не указал(а), попробуй снова с помощью /beer')
    else:
        bot.send_message(message.chat.id, f'Следующая встреча состоится в {place}, {time}')



bot.infinity_polling()