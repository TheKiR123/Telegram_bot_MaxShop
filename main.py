import telebot
import sqlite3
from telebot import types
from datetime import date
from string import punctuation

from telebot.types import InputMediaPhoto

bot = telebot.TeleBot('6457181720:AAH2eDiXF70Z7RvdkDkndmgEaDEb2Aeoovs')
product = []

message_order_list = ['Тип доставки: ', 'Имя Фамилия: ', 'Номер телефона: ', 'Город проживания: ', 'Отделение '
                                                                                                   'европочты/адрес '
                                                                                                   'проживания:',
                      'Товар: ', 'Итоговая цена: ', 'Ник заказчика @']

states = {
    'start': 0,
    'watch_selected': 1,
    'earphones_selected': 2,
    'attachment_selected': 3,
    'watch_model_selected': 4,
    'earphones_model_selected': 5,
    'attachment_model_selected': 6,
    'order': 7,
    'sending_order': 8,
    'chose_sell': 9,
    'show_sell_model': 10,
    'full_sell_model_info': 11,
}

sell_offers = {
    '1': ["Air pods pro2(с шумкой) + Часы HK9PRO(watch8 45mm)", 250, 'watch', 'earphones'],
    '2': ['Air pods pro2(с шумкой) + Часы HK8PRO MAX(watch ultra 49mm)', 260, 'watch', 'earphones'],
    '3': ['Air pods 3 + Часы HK9PRO(watch8 45mm)', 230, 'watch', 'earphones'],
    '4': ['Air pods 3 + Часы HK8PRO MAX(watch ultra 49mm)', 240, 'watch', 'earphones'],
    '5': ['Часы HK9PRO(watch8 45mm) + Часы HK8PRO MAX(watch ultra 49mm)', 280, 'earphones', 'earphones']
}

punctuation += '№'

add_model = False

user_state = {}

orders = {}

selected_models = {}

alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def hello_command(name):
    return f'Привет {name}, я бот магазина airzone и я помогу тебе определиться с выбором и сделать заказ. Какой из ' \
           f'видов ' \
           f'товара тебя интересует?'

def zapros(table_name: str, first_str: str, second_str: str) -> tuple:
    profuct_dict = {}
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} WHERE quantity > 0')
    data = cursor.fetchall()
    info = ''
    count = 1
    info += first_str
    for i in data:
        profuct_dict[count] = i[0]
        if i[1] not in product:
            product.append(i[1])
        info += f'{i[0]}.{i[1]}\n✅{i[3]} рублей❌вместо {i[5]}\n\n'
        count += 1
    info += second_str
    cursor.close()
    conn.close()
    return (info, profuct_dict)

def get_model(table_name: str, model_name: int, products: dict) -> tuple:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} WHERE quantity > 0 and id =\'{products[model_name]}\'')
    data = cursor.fetchall()
    info = ''
    for i in data:
        info += f'{i[1]}\n{i[2]}\n\n✅{i[3]} рублей❌вместо {i[5]}\n\n'
    cursor.close()
    conn.close()
    return info, data

def get_sale_model(table_name: str, model_name: str):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} WHERE quantity > 0 and name =\'{model_name}\'')
    data = cursor.fetchall()
    info = ''
    for i in data:
        info += f'{i[1]}\n{i[2]}\n\n✅{i[3]} рублей❌вместо {i[5]}\n\n'
    cursor.close()
    conn.close()
    return info, data[0][-1]

def add_order(text: list, models: str, price: int):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        name = text[1].split(' ')[0]
        surname = text[1].split(' ')[1]
        number = text[2]
        time = date.today()
        final = []
        for i in text:
            final.append(i)
        final.append(models)
        final.append(price)
        cursor.execute(f'insert into orders(type_of_delivery, name, surname, phone_number, city, adress, models, price, '
                    f'date_time'
                    f') values ('
                    f'\'{text[0]}\', '
                    f'\'{name}\', \'{surname}\', \'{number}\', \'{text[3]}\', \'{text[4]}\', \'{models}\', {price}, '
                    f'\'{time}\')')
        conn.commit()
        cursor.close()
        conn.close()
        return final
    except Exception as ex:
        print(ex)

def get_sell():
    info = ''
    for key, value in sell_offers.items():
        info += f'{key}. {value[0]} - {value[1]} рублей\n'
    return info

@bot.message_handler(commands=['start'])
def hello(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    watch = types.KeyboardButton('Часы⌚️')
    earphones = types.KeyboardButton('Наушники🎧')
    attachment = types.KeyboardButton('Аксессуары🔋')
    markup.add(watch, earphones, attachment)
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Привет {name}, я бот магазина airzone и я помогу тебе определиться с '
                                      f'выбором и '
                                      f'сделать заказ. Какой из видов товара тебя интересует?', reply_markup=markup)
    user_state[message.chat.id] = states['start']

@bot.message_handler(content_types=['text'])
def start_reply(message):
    chat_id = message.chat.id
    try:
        if user_state[chat_id] == states['start']:
            if message.text == 'Часы⌚️':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад🔙')
                markup.add(back)
                bot.send_message(chat_id, zapros('earphones', 'Отлично!\nВот список имеющихся в наличии часов:\n\n',
                                                 'В комплекте с часами: \n• Беспроводная зарядка\n• Силиконовый ремешок в цвет корпуса часов, как на фото\nЗаинтересовала определенная модель? Укажи ее номер')[0], reply_markup=markup)
                user_state[chat_id] = states['watch_selected']
            elif message.text == 'Наушники🎧':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад🔙')
                markup.add(back)
                bot.send_message(chat_id, zapros('watch', 'Отлично!\nВот список имеющихся в наличии наушников:\n\n',
                                                 'К наушникам дарим защитный чехол!🎁\nЗаинтересовала определенная модель? Укажи ее номер')[0], reply_markup=markup)
                user_state[chat_id] = states['earphones_selected']
            elif message.text == 'Аксессуары🔋':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад🔙')
                markup.add(back)
                bot.send_message(chat_id, zapros('attachment', 'Отлично!\nВот список имеющихся в наличии '
                                                               'аксессуаров:\n\n', 'Заинтересовала определенная модель? '
                                                                                   'Укажи ее номер')[0],
                                 reply_markup=markup)
                user_state[chat_id] = states['attachment_selected']
            elif message.text == 'Начать с начала':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                watch = types.KeyboardButton('Часы⌚️')
                earphones = types.KeyboardButton('Наушники🎧')
                attachment = types.KeyboardButton('Аксессуары🔋')
                markup.add(watch, earphones, attachment)
                name = message.from_user.first_name
                bot.send_message(message.chat.id,
                                 f'Привет {name}, я бот магазина airzone и я помогу тебе определиться с '
                                 f'выбором и '
                                 f'сделать заказ. Какой из видов товара тебя интересует?', reply_markup=markup)


        elif (user_state[chat_id] == states['watch_selected'] or user_state[chat_id] == states['earphones_selected'] or user_state[chat_id]\
                == states['attachment_selected']) and message.text == 'Назад🔙':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            watch = types.KeyboardButton('Часы⌚️')
            earphones = types.KeyboardButton('Наушники🎧')
            attachment = types.KeyboardButton('Аксессуары🔋')
            markup.add(watch, earphones, attachment)
            bot.send_message(chat_id, hello_command(message.from_user.first_name), reply_markup=markup)
            user_state[message.chat.id] = states['start']


#
#          ЧАСЫ !!!
#


        elif user_state[chat_id] == states['watch_selected']:
            my_tuple = zapros('earphones', 'Отлично!\nВот список имеющихся в наличии часов:\n\n',
                                                 'В комплекте с часами: \n• Беспроводная зарядка\n• Силиконовый ремешок в цвет корпуса часов, как на фото\nЗаинтересовала определенная модель? Укажи ее номер')
            try:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад к часам🔙')
                order = types.KeyboardButton('Заказать😊')
                markup.add(back, order)
                model = get_model('earphones', int(message.text), my_tuple[1])
                photos = model[1][0][-1].split(' ')
                photo1 = photos[0]
                photo2 = photos[1]
                media = [InputMediaPhoto(open(f'./{photo1}', 'rb'), caption=f'{model[0]}'),
                         InputMediaPhoto(open(f'./{photo2}', 'rb'))]
                bot.send_media_group(chat_id, media)
                bot.send_message(chat_id, text='Заинтересовало предложение? Жми "заказать"👇🏻', reply_markup=markup,
                                 disable_notification=True)
                user_state[chat_id] = states['watch_model_selected']
                selected_models[chat_id] = {model[1][0][1]: model[1][0]}
            except Exception as ex:
                bot.send_message(chat_id, "Похоже вы неправильно ввели номер модели, требуется только число")
                print(ex)


        elif user_state[chat_id] == states['watch_model_selected']:
            if message.text == 'Назад к часам🔙':
                my_tuple = zapros('earphones', 'Отлично!\nВот список имеющихся в наличии часов:\n\n',
                                  'В комплекте с часами: \n• Беспроводная зарядка\n• Силиконовый ремешок в цвет корпуса часов, как на фото\nЗаинтересовала определенная модель? Укажи ее номер')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад🔙')
                markup.add(back)
                bot.send_message(chat_id, my_tuple[0], reply_markup=markup)
                user_state[chat_id] = states['watch_selected']
                if not add_model:
                    del selected_models[chat_id]
            elif message.text == 'Заказать😊':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                still_order = types.KeyboardButton('Оставить выбранное')
                sale = types.KeyboardButton('Акция')
                markup.add(sale, still_order)
                bot.send_message(chat_id, 'Также мы подготовили 2 СПЕЦПРЕДЛОЖЕНИЯ на комплекты 1+1 🔥\n\n1️⃣Часы + '
                                          'наушники будут по СПЕЦИАЛЬНОЙ цене Air pods pro2(с шумкой) + Часы HK9PRO('
                                          'watch8 45mm) - 250 рублей\n Air pods pro2(с шумкой) + Часы HK8PRO MAX(watch '
                                          'ultra 49mm) - 260 рублей\n Air pods 3 + Часы HK9PRO(watch8 45mm) - 230 '
                                          'рублей\n Air pods 3 + Часы HK8PRO MAX(watch ultra 49mm) - 240 рублей\n\n '
                                          '2️⃣Часы + часы по СПЕЦИАЛЬНОЙ цене\n HK9PRO(watch8 45mm) + Часы HK8PRO MAX('
                                          'watch ultra 49mm)- 280 рублей', reply_markup=markup)
                user_state[chat_id] = states['order']



#
#          НАУШНИКИ !!!
#


        elif user_state[chat_id] == states['earphones_selected']:
            my_tuple = zapros('watch', 'Отлично!\nВот список имеющихся в наличии наушников:\n\n',
                                                 'К наушникам дарим защитный чехол!🎁\nЗаинтересовала определенная модель? Укажи ее номер')
            try:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад к наушникам🔙')
                order = types.KeyboardButton('Заказать😊')
                markup.add(back, order)
                model = get_model('watch', int(message.text), my_tuple[1])
                photos = model[1][0][-1].split(' ')
                photo1 = photos[0]
                photo2 = photos[1]
                media = [InputMediaPhoto(open(f'./{photo1}', 'rb'), caption=f'{model[0]}'),
                         InputMediaPhoto(open(f'./{photo2}', 'rb'))]
                bot.send_media_group(chat_id, media)
                bot.send_message(chat_id, text='Заинтересовало предложение? Жми "заказать"👇🏻', reply_markup=markup,
                                 disable_notification=True)
                user_state[chat_id] = states['earphones_model_selected']
                selected_models[chat_id] = {model[1][0][1]: model[1][0]}
            except Exception as ex:
                bot.send_message(chat_id, "Похоже вы неправильно ввели номер модели, требуется только номер")
                print(ex)


        elif user_state[chat_id] == states['earphones_model_selected']:
            if message.text == 'Назад к наушникам🔙':
                my_tuple = zapros('watch', 'Отлично!\nВот список имеющихся в наличии наушников:\n\n',
                                  'К наушникам дарим защитный чехол!🎁\nЗаинтересовала определенная модель? Укажи ее номер')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад🔙')
                markup.add(back)
                bot.send_message(chat_id, my_tuple[0], reply_markup=markup)
                user_state[chat_id] = states['earphones_selected']
                if not add_model:
                    del selected_models[chat_id]
            elif message.text == 'Заказать😊':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                still_order = types.KeyboardButton('Оставить выбранное')
                sale = types.KeyboardButton('Акция')
                markup.add(sale, still_order)
                bot.send_message(chat_id, 'Также мы подготовили 2 СПЕЦПРЕДЛОЖЕНИЯ на комплекты 1+1 🔥\n\n1️⃣Часы + '
                                          'наушники будут по СПЕЦИАЛЬНОЙ цене Air pods pro2(с шумкой) + Часы HK9PRO('
                                          'watch8 45mm) - 250 рублей\n Air pods pro2(с шумкой) + Часы HK8PRO MAX(watch '
                                          'ultra 49mm) - 260 рублей\n Air pods 3 + Часы HK9PRO(watch8 45mm) - 230 '
                                          'рублей\n Air pods 3 + Часы HK8PRO MAX(watch ultra 49mm) - 240 рублей\n\n '
                                          '2️⃣Часы + часы по СПЕЦИАЛЬНОЙ цене\n HK9PRO(watch8 45mm) + Часы HK8PRO MAX('
                                          'watch ultra 49mm)- 280 рублей', reply_markup=markup)
                user_state[chat_id] = states['order']



#
#          АКСЕССУАРЫ !!!
#

        elif user_state[chat_id] == states['attachment_selected']:
            my_tuple = zapros('attachment', 'Отлично!\nВот список имеющихся в наличии аксессуаров:\n\n',
                              'Заинтересовала определенная модель? '
                              'Укажи ее номер')
            try:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад к аксессуарам🔙')
                order = types.KeyboardButton('Заказать😊')
                markup.add(back, order)
                model = get_model('attachment', int(message.text), my_tuple[1])
                photos = model[1][0][-1].split(' ')
                if len(photos) == 1:
                    photo1 = photos[0]
                    media = [InputMediaPhoto(open(f'./{photo1}', 'rb'), caption=f'{model[0]}')]
                    bot.send_media_group(chat_id, media)
                    bot.send_message(chat_id, text='Заинтересовало предложение? Жми "заказать"👇🏻', reply_markup=markup,
                                     disable_notification=True)
                else:
                    photo1 = photos[0]
                    photo2 = photos[1]
                    media = [InputMediaPhoto(open(f'./{photo1}', 'rb'), caption=f'{model[0]}'),
                             InputMediaPhoto(open(f'./{photo2}', 'rb'))]
                    bot.send_media_group(chat_id, media)
                    bot.send_message(chat_id, text='Заинтересовало предложение? Жми "заказать"👇🏻', reply_markup=markup,
                                     disable_notification=True)
                user_state[chat_id] = states['attachment_model_selected']
                selected_models[chat_id] = {model[1][0][1]: model[1][0]}
            except Exception:
                bot.send_message(chat_id, "Похоже вы неправильно ввели номер, требуется только номер")


        elif user_state[chat_id] == states['attachment_model_selected']:
            if message.text == 'Назад к аксессуарам🔙':
                my_tuple = zapros('attachment', 'Отлично!\nВот список имеющихся в наличии аксессуаров:\n\n',
                                  'Заинтересовала определенная модель? '
                                  'Укажи ее номер')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад🔙')
                markup.add(back)
                bot.send_message(chat_id, my_tuple[0], reply_markup=markup)
                user_state[chat_id] = states['attachment_selected']
                if not add_model:
                    del selected_models[chat_id]
            elif message.text == 'Заказать😊':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                still_order = types.KeyboardButton('Оставить выбранное')
                sale = types.KeyboardButton('Акция')
                markup.add(sale, still_order)
                bot.send_message(chat_id, 'Также мы подготовили 2 СПЕЦПРЕДЛОЖЕНИЯ на комплекты 1+1 🔥\n\n1️⃣Часы + '
                                          'наушники будут по СПЕЦИАЛЬНОЙ цене Air pods pro2(с шумкой) + Часы HK9PRO('
                                          'watch8 45mm) - 250 рублей\n Air pods pro2(с шумкой) + Часы HK8PRO MAX(watch '
                                          'ultra 49mm) - 260 рублей\n Air pods 3 + Часы HK9PRO(watch8 45mm) - 230 '
                                          'рублей\n Air pods 3 + Часы HK8PRO MAX(watch ultra 49mm) - 240 рублей\n\n '
                                          '2️⃣Часы + часы по СПЕЦИАЛЬНОЙ цене\n HK9PRO(watch8 45mm) + Часы HK8PRO MAX('
                                          'watch ultra 49mm)- 280 рублей', reply_markup=markup)
                user_state[chat_id] = states['order']


#
#          ЗАКАЗ
#

        elif user_state[chat_id] == states['order']:
            if message.text == 'Оставить выбранное':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                prim = types.KeyboardButton('Пример заполнения')
                markup.add(prim)
                bot.send_message(chat_id, '1) европочта/курьер \n2) имя фамилия \n3)номер телефона \n4) Город '
                                          'проживания\n5) отделение '
                                          'европочты/адрес проживания', reply_markup=markup)
                user_state[chat_id] = states['sending_order']
            elif message.text == 'Акция':
                info = get_sell()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Оставить выбранный товар')
                markup.add(back)
                bot.send_message(chat_id, f'Прекрасно, укажите пожалуйста номер интересующей позиции\n{info}',
                                 reply_markup=markup)
                user_state[chat_id] = states['chose_sell']

        elif user_state[chat_id] == states['sending_order']:
            if message.text == 'Пример заполнения':
                bot.send_message(chat_id, 'Европочта/Доставка\nИванов Иван\n+375 (33) 333-33-33\nг.Минск\n Отделение '
                                          '№1/ул.Молодежная д.1 кв.1')
            elif message.text == 'Назад к акции':
                info = get_sell()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                still = types.KeyboardButton('Оставить выбранный товар')
                markup.add(still)
                bot.send_message(chat_id, f'Прекрасно, укажите пожалуйста номер интересующей позиции\n{info}',
                                 reply_markup=markup)
                user_state[chat_id] = states['chose_sell']
            else:
                try:
                    txt = message.text
                    data = txt.split('\n')
                    exception_list = ''
                    if len(data) != 5:
                        raise Exception('Недостаточно данных. Убедитесь что вы ввели всю информацию и ничего лишнего')

                    #Проверка выбора доставки
                    for i in data[0]:
                        if i not in alphabet and i not in alphabet.upper():
                            if '❌ В первой строке должны быть только буквы\n\n' in exception_list:
                                break
                            exception_list += '❌ В первой строке должны быть только буквы\n\n'

                    #Проверка имени и фамилии
                    name = data[1].split(' ')
                    for i in name:
                        for j in i:
                            if j not in alphabet and j not in alphabet.upper():
                                if '❌ В строке имени и фамилии должны быть только имя и фамилия без ' \
                                                  'других символов\n\n' in exception_list:
                                    break
                                exception_list += '❌ В строке имени и фамилии должны быть только имя и фамилия без ' \
                                                  'других символов\n\n'

                    #Проверка номера телефона
                    for i in data[2]:
                        if not i.isdigit() and i != ' ' and i != '-' and i != '+' and i != '(' and i != ')':
                            if '❌ Неправильный ввод номера телефона. Сморите пример ввода данных\n\n' in exception_list:
                                break
                            exception_list += '❌ Неправильный ввод номера телефона. Сморите пример ввода данных\n\n'

                    #Проверка города
                    for i in data[3]:
                        if i not in alphabet and i != '.':
                            if '❌ Неправильный ввод города' in exception_list:
                                break
                            exception_list += '❌ Неправильный ввод города'


                    if len(exception_list) > 0:
                        raise Exception(exception_list)
                    price = 0
                    model_list = []
                    if 'sell' in selected_models[chat_id].keys():
                        models = selected_models[chat_id]['sell'][0]
                        price = selected_models[chat_id]['sell'][1]
                    else:
                        for i in selected_models[chat_id].values():
                            price += i[3]
                            model_list.append(i[1])
                        models = ''
                        for i in model_list:
                            models += i
                            models += ' '
                    info = add_order(data, models, price)
                    maxim_message = 'Новый заказ пришел, зайка\n'
                    count = 0
                    for i in info:
                        if count < len(message_order_list) - 1:
                            mes = message_order_list[count] + str(i) + '\n'
                            maxim_message += mes
                            count += 1
                        else:
                            maxim_message += str(i)
                            maxim_message += '\n'
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    start = types.KeyboardButton('Начать с начала')
                    markup.add(start)
                    bot.send_message(349264741, maxim_message + message_order_list[-1] + message.from_user.username)
                    bot.send_message(chat_id, 'Большое спасибо за заказ\nВ скором времени с вами свяжутся для подтверждения '
                                              'заказа', reply_markup=markup)
                    user_state[chat_id] = states['start']
                except Exception as ex:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    prim = types.KeyboardButton('Пример заполнения')
                    markup.add(prim)
                    bot.send_message(chat_id, str(ex), reply_markup=markup)


#
#     АКЦИЯ
#

        elif user_state[chat_id] == states['chose_sell']:
            if message.text == 'Оставить выбранный товар':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                prim = types.KeyboardButton('Пример заполнения')
                back = types.KeyboardButton('Назад к акции')
                markup.add(back, prim)
                bot.send_message(chat_id, '1) европочта/курьер \n2) имя фамилия \n3)номер телефона \n4) Город '
                                          'проживания\n5) отделение '
                                          'европочты/адрес проживания\nЕблан, пиши данные в столбик как в примере или ты вообще аутист бездарный и по примеру ебаному непонятно',reply_markup=markup)
                if 'sell' in selected_models[chat_id].keys():
                    del selected_models[chat_id]['sell']
                user_state[chat_id] = states['sending_order']
            else:
                try:
                    if message.text in sell_offers.keys():
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        back = types.KeyboardButton('Назад')
                        order = types.KeyboardButton('Заказать')
                        markup.add(back, order)
                        bot.send_message(chat_id, f'Вы выбрали пару {sell_offers[message.text][0]} за '
                                                  f'{sell_offers[message.text][1]} рублей\nЧтобы узнать '
                                                  f'подробнее '
                                                  f'об определенной модели укажите пожалуйста полностью модель',
                                         reply_markup=markup)
                        selected_models[chat_id]['sell'] = [sell_offers[message.text][0], sell_offers[message.text][
                            1], sell_offers[message.text][2], sell_offers[message.text][3]]
                        user_state[chat_id] = states['show_sell_model']
                    else:
                        bot.send_message(chat_id, 'Похоже вы неправильно ввели несуществующий в списке номер')
                except Exception:
                    bot.send_message(chat_id, 'Похоже вы неправильно ввели номер, требуется только номер')

        elif user_state[chat_id] == states['show_sell_model']:
            if message.text == 'Заказать':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                prim = types.KeyboardButton('Пример заполнения')
                markup.add(prim)
                bot.send_message(chat_id, '1) европочта/курьер \n2) имя фамилия \n3)номер телефона \n4) Город '
                                          'проживания\n5) отделение '
                                          'европочты/адрес проживания',
                                 reply_markup=markup)
                user_state[chat_id] = states['sending_order']
            elif message.text == 'Назад':
                info = get_sell()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                prev = types.KeyboardButton('Оставить выбранный товар')
                markup.add(prev)
                bot.send_message(chat_id, f'Прекрасно, укажите пожалуйста номер интересующей позиции\n{info}',
                                 reply_markup=markup)
                if 'sell' in selected_models[chat_id].keys():
                    del selected_models[chat_id]['sell']
                user_state[chat_id] = states['chose_sell']
            else:
                try:
                    names = selected_models[chat_id]['sell'][0].split('+')
                    if message.text == names[0][:-1]:
                        table = selected_models[chat_id]['sell'][2]
                    else:
                        table = selected_models[chat_id]['sell'][3]
                    info = get_sale_model(table, message.text)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    back = types.KeyboardButton('Назад к паре')
                    markup.add(back)
                    photos = info[1].split(' ')
                    photo1 = photos[0]
                    photo2 = photos[1]
                    media = [InputMediaPhoto(open(f'./{photo1}', 'rb'), caption=f'{info[0]}'),
                             InputMediaPhoto(open(f'./{photo2}', 'rb'))]
                    bot.send_media_group(chat_id, media)
                    bot.send_message(chat_id, text='🔎',
                                     reply_markup=markup,
                                     disable_notification=True)
                    user_state[chat_id] = states['full_sell_model_info']
                except Exception as ex:
                    bot.send_message(chat_id, 'Требуется ввести полное название модели')
                    print(ex)

        elif user_state[chat_id] == states['full_sell_model_info']:
            if message.text == 'Назад к паре':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton('Назад')
                order = types.KeyboardButton('Заказать')
                markup.add(back, order)
                sell = 'sell'
                bot.send_message(chat_id, f'Вы выбрали пару {selected_models[chat_id][sell][0]} за '
                                          f'{selected_models[chat_id][sell][1]} рублей\nЧтобы узнать '
                                          f'подробнее '
                                          f'об определенной модели укажите пожалуйста полностью модель',
                                 reply_markup=markup)
                user_state[chat_id] = states['show_sell_model']


    except Exception:
        bot.send_message(chat_id, 'К сожалению возникла ошибка\nДля возобновления работы введите /start')


bot.polling(none_stop=True)