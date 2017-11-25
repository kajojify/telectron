yandex_apikey = ""
bot_token = ""
google_apikey = ""


flags = {
    'ua': str(b'\xf0\x9f\x87\xba\xf0\x9f\x87\xa6', 'utf-8'),
    'ru': str(b'\xf0\x9f\x87\xb7\xf0\x9f\x87\xba', 'utf-8'),
    'by': str(b'\xf0\x9f\x87\xa7\xf0\x9f\x87\xbe', 'utf-8'),
    'kz': str(b'\xf0\x9f\x87\xb0\xf0\x9f\x87\xbf', 'utf-8'),
    'lt': str(b'\xf0\x9f\x87\xb1\xf0\x9f\x87\xb9', 'utf-8'),
    'tr': str(b'\xf0\x9f\x87\xb9\xf0\x9f\x87\xb7', 'utf-8'),
    'am': str(b'\xf0\x9f\x87\xa6\xf0\x9f\x87\xb2', 'utf-8'),
}

ukraine = flags['ua'] + " Украина"
russia = flags['ru'] + " Россия"
belarus = flags['by'] + " Беларусь"
kazakhstan = flags['kz'] + " Казахстан"
lithuania = flags['lt'] + " Литва"
turkey = flags['tr'] + " Турция"
armenia = flags['am'] + " Армения"

countries = [ukraine, russia, belarus, kazakhstan, lithuania, turkey, armenia]
country_numbers = {'Украина': 0, 'Россия': 1, 'Беларусь': 2, 'Казахстан': 3,
                   'Литва': 4, 'Турция': 5, 'Армения': 6}


emojis = {
    'plus': str(b'\xe2\x9e\x95', 'utf-8'),
    'back': str(b'\xf0\x9f\x94\x99', 'utf-8'),
    'info': str(b'\xe2\x84\xb9\xef\xb8\x8f', 'utf-8'),
    'list': str(b'\xf0\x9f\x93\x9d', 'utf-8'),
    'gear': str(b'\xe2\x9a\x99\xef\xb8\x8f', 'utf-8'),
    'forward': str(b'\xe2\xac\x86\xef\xb8\x8f', 'utf-8'),
    'backward': str(b'\xe2\xac\x87\xef\xb8\x8f', 'utf-8'),
    'radar': str(b'\xf0\x9f\x93\xa1', 'utf-8'),
    'hand': str(b'\xf0\x9f\x96\x90', 'utf-8'),
    'rounded_arrow': str(b'\xe2\x86\xa9\xef\xb8\x8f', 'utf-8'),
    'globe': str(b'\xf0\x9f\x8c\x90', 'utf-8'),
    'bot': str(b'\xf0\x9f\xa4\x96', 'utf-8'),
    'author': str(b'\xf0\x9f\x91\xa4', 'utf-8'),
    'notebook': str(b'\xf0\x9f\x93\x8b', 'utf-8'),
    'earth': str(b'\xf0\x9f\x8c\x8d', 'utf-8'),
    'bell': str(b'\xf0\x9f\x94\x94', 'utf-8'),
    'red_cross': str(b'\xe2\x9d\x8c', 'utf-8'),
    'schedule': str(b'\xf0\x9f\x93\x8b', 'utf-8')
}

buttons = {
    'new_route': emojis['plus'] + " Новый маршрут",
    'my_routes': emojis['list'] + " Мои маршруты",
    'settings': emojis['gear'] + " Настройки",
    'additional_info': emojis['info'] + " Доп. информация",
    'comeback': emojis['back'] + " Назад",
    'departure': emojis['forward'] + " Станция отправления",
    'arrival': emojis['backward'] + " Станция прибытия",
    'manual_input': emojis['hand'] + " Ввести вручную",
    'geolocation': emojis['radar'] + " По геопозиции",
    'send_geolocation': emojis['globe'] + " Отправить местоположение",
    'about_bot': emojis['bot'] + " О боте",
    'about_author': emojis['author'] + " Об авторе",
    'change_country': emojis['earth'] + " Изменить страну",
    'notifications': emojis['bell'] + " Мои оповещения",
    'schedule': emojis['schedule'] + " Расписание",
    'nearest': 'Ближайшее',
    'today': 'На сегодня',
    'tomorrow': 'На завтра',
    'entire': 'На все дни',
    'set_notifications': emojis['bell'] + " Создать оповещение"
}

comeback_button = {"new_route": "main_menu", "my_routes": "main_menu", 'notifications': 'main_menu',
                   "settings": "main_menu", 'additional_info': 'main_menu',
                   "arrival": "new_route", "departure": "new_route", 'departure_input': 'departure',
                   'arrival_input': 'arrival', 'specify_departure_region': 'departure',
                   'specify_arrival_region': 'arrival', 'specify_arrival_station': 'arrival',
                   'specify_departure_station': 'departure', 'already_set_arrival': 'main_menu',
                   'already_set_departure': 'main_menu', 'arrival_region': 'new_route',
                   'departure_region': 'new_route', 'specify_radius_dep': 'departure',
                   'specify_radius_arr': 'arrival', 'change_country': 'main_menu', 'created_route': 'main_menu',
                   'when_closings': 'main_menu', 'when_schedule': 'main_menu', 'entire_schedule': 'main_menu',
                   'schedule': 'main_menu'}

additional_info = {'about_bot': "Данные предоставлены сервисом [Яндекс.Расписания](https://rasp.yandex.ru/)\n"
                                "А здесь я расскажу о том, что бот умеет...",
                   'about_author': "\nС разработчиком можно связаться посредством:\n"
                                   "1. email - ttahabatt@gmail.com\n"
                                   "2. telegram - @kajojify"}

permitted_states = {
    "main_menu": {'keyboard': 'reply',
                  'buttons': [buttons['new_route'], buttons['my_routes'],
                              buttons['notifications'], buttons['settings'],
                              buttons['additional_info']],
                  'message': {'no_routes': "Привет! Я - *Тэлектрон*.\n"
                                           "Давайте помогу Вам с электричками!\n\n"
                                           "1. Создайте *Новый маршрут*.\n"
                                           "2. Просматривайте расписания и отмены на этот маршрут, "
                                           "получайте оповещения о любой электричке из расписания и многое другое.\n\n"
                                           "*Подробнее обо мне и моих возможностях:*\n"
                                           "_Доп. информация_ -> _О боте_",
                              'routes': "Давайте помогу Вам с электричками!\n\n"
                                        "Просматривайте расписания и закрытия на любой из сохраненных Вами маршрутов:\n"
                                        "_Мои маршруты_ -> _Введите номер маршрута_\n\n"
                                        "*Подробнее обо мне и моих возможностях:*\n"
                                        "_Доп. информация_ -> _О боте_"}},

    "new_route": {'keyboard': 'reply',
                  'buttons': [buttons['departure'], buttons['arrival'],
                              buttons['comeback']],
                  'message': "Укажите *станцию отправления* и *станцию прибытия*."},

    "my_routes": {'keyboard': 'reply',
                  'buttons': [buttons['comeback']],
                  'message': "Здесь будут все созданные тобой маршруты!"},

    'notifications': {'keyboard': 'reply',
                  'buttons': [buttons['comeback']],
                  'message': "Здесь будут все твои оповещения!"},

    "settings": {'keyboard': 'reply',
                 'buttons': [buttons['change_country'],
                             buttons['comeback']],
                 'message': "Здесь будут настройки!"},

    "additional_info": {'keyboard': 'reply',
                        'buttons': [buttons['about_bot'], buttons['about_author'],
                                    buttons['comeback']],
                        'message': 'О чем Вы хотите узнать поподробнее?'},

    "departure": {'keyboard': 'reply',
                  'buttons': [buttons['manual_input'],
                              buttons['geolocation'],
                              buttons['comeback']],
                  'message': '*Станцию отправления* будете задавать вручную или по геопозиции?'},

    "arrival": {'keyboard': 'reply',
                'buttons': [buttons['manual_input'],
                            buttons['geolocation'],
                            buttons['comeback']],
                'message': '*Станцию прибытия* будете задавать вручную или по геопозиции?'},

    "already_set_arrival": {'message': 'Вы уже указали *станцию прибытия*!'},

    "already_set_departure": {'message': 'Вы уже указали *станцию отправления*!'},

    "arrival_input": {'keyboard': 'inline',
                      'buttons': countries,
                      'message': ["Выберете _страну_, в которой находится *станция отправления*.\n"
                                  "В дальнейшем она будет использована *по умолчанию* "
                                  "и её можно будет изменить в настройках.",
                                  "Ваша страна:"]},

    "departure_input": {'keyboard': 'inline',
                        'buttons': countries,
                        'message': ["Выберете _страну_, в которой находится *станция прибытия*.\n"
                                    "В дальнейшем она будет использована *по умолчанию* "
                                    "и её можно будет изменить в настройках.",
                                    "Ваша страна:"]},

    "change_country": {'keyboard': 'inline',
                        'buttons': countries,
                        'message': ["Выберете другую страну пребывания.",
                                    "Ваша страна:"]},

    "specify_departure_region": {'keyboard': 'inline',
                                 'message': ["Выберете первую букву региона(области),"
                                             " в котором находится *станция отправления.*",
                                             "Ваш регион отправления:"]},

    "specify_arrival_region": {'keyboard': 'inline',
                               'message': ["Выберете первую букву региона(области),"
                                           " в котором находится *станция прибытия.*",
                                           "Ваш регион прибытия:"]},

    "specify_arrival_station": {'keyboard': 'none',
                                'message': "Напечатайте название *станции прибытия*.\n"
                                           "Например: 205 км, Екатеринбург-Пасс., Иваново"},

    "specify_departure_station": {'keyboard': 'none',
                                  'message': "Напечатайте название *станции отправления*.\n"
                                             "Например: 198 км, Пятихатки-Пасс., Екатериновка"},

    "arrival_region": {'keyboard': 'inline'},

    "departure_region": {'keyboard': 'inline'},

    "check_values": {'keyboard': 'none',
                     'message': 'К сожалению, станция не найдена! Попробуйте снова.'},

    "clarify_arrival_direction": {},

    "clarify_departure_direction": {},

    "print_schedule": {},

    "specify_radius_dep": {'message': ['Отправьте текущую геопозицию, нажав кнопку\n_Отправить местоположение_.\n'
                                       'Или прикрепите любую геопозицию с помощью \U0001f4ce.\n\n'
                                       'Задайте радиус поиска Вашей *станции отправления*.\n'
                                       '*min* радиус - 1 км\n*max* радиус - 20 км.',
                                       'Радиус поиска   -  *5 км*']},

    'specify_radius_arr': {'message': ['Отправьте текущую геопозицию, нажав кнопку\n_Отправить местоположение_.\n'
                                       'Или прикрепите любую геопозицию с помощью \U0001f4ce.\n\n'
                                       'Задайте радиус поиска Вашей *станции прибытия*.\n'
                                       '*min* радиус - 1 км\n*max* радиус - 20 км.',
                                       'Радиус поиска   -  *5 км*']},

    'sure_arr': {},

    'sure_dep': {},

    'choose_subtrain': {},

    'created_route': {'keyboard': 'reply',
                      'message': 'На когда Вам показать расписание?',
                      'buttons': [buttons['schedule'],
                                  buttons['departure'], buttons['arrival'],
                                  buttons['comeback']]},

    'schedule': {'keyboard': 'reply',
                 'message': 'На когда Вам показать расписание?',
                 'buttons': [buttons['nearest'], buttons['today'], buttons['tomorrow'],
                                  buttons['entire'],
                                  buttons['comeback']]},

    'to_my_route': {'keyboard': 'none',
         'message': 'Ваш маршрут добавлен в _Мои маршруты_!'},

    'entire_schedule': {'keyboard': 'reply',
                        'buttons': [buttons['set_notifications'], buttons['comeback']]},

    'today_schedule': {'keyboard': 'reply',
                       'buttons': [buttons['set_notifications'], buttons['comeback']]},

    'tomorrow_schedule': {'keyboard': 'reply',
                          'buttons': [buttons['set_notifications'], buttons['comeback']]},

    'routes': {},

    'nearest_schedule': {'keyboard': 'reply',
                          'buttons': [buttons['set_notifications'], buttons['comeback']]},

    'specific_route': {'keyboard': 'none'}
    }
