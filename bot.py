import json

import telebot

import config
import yandex_api
import redis_utils


bot = telebot.TeleBot(config.bot_token)
redis = redis_utils.Redis()
changer = redis_utils.StateChanger(bot, redis)
handler = redis_utils.DataHandler(bot, redis)


@bot.message_handler(commands=['start'])
def start(message):
    changer.go_into_state(message.from_user.id, "main_menu")


#########################################
############### main_menu ###############

@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) == "main_menu")
def new_route(message):
    if message.text == config.buttons['new_route']:
        changer.go_into_state(message.from_user.id, "new_route")
    elif message.text == config.buttons['my_routes']:
        changer.go_into_state(message.from_user.id, "my_routes")
    elif message.text == config.buttons['notifications']:
        changer.go_into_state(message.from_user.id, "notifications")
    elif message.text == config.buttons['settings']:
        changer.go_into_state(message.from_user.id, "settings")
    elif message.text == config.buttons['additional_info']:
        changer.go_into_state(message.from_user.id, "additional_info")
    else:
        bot.send_message(message.from_user.id, "Неверный ввод!"
                                               " Нажмите на одну из кнопок меню.")


@bot.message_handler(func=lambda m: m.text == config.buttons['comeback'] and
                                    changer.get_state(m.from_user.id) in config.comeback_button)
def comeback(message):
    state = changer.get_state(message.from_user.id)
    comebacking_state = config.comeback_button[state]

    changer.go_into_state(message.from_user.id, comebacking_state)


#########################################
################ new_route ##############

@bot.callback_query_handler(func=lambda c: c.data == "Всё равно продолжить")
def station_specifying(c):
    if changer.get_state(c.from_user.id) == "already_set_departure":
        changer.go_into_state(c.from_user.id, "departure")
    else:
        changer.go_into_state(c.from_user.id, "arrival")


@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) in ["new_route",
                                                                          "already_set_departure",
                                                                          "already_set_arrival"])
def station_specifying(message):
    if message.text == config.buttons['departure']:
        if redis.hexists(message.from_user.id, "dep_code"):
            changer.already_set_direction(message.from_user.id, "already_set_departure")
        else:
            changer.go_into_state(message.from_user.id, "departure")
    elif message.text == config.buttons['arrival']:
        if redis.hexists(message.from_user.id, "arr_code"):
            changer.already_set_direction(message.from_user.id, "already_set_arrival")
        else:
            changer.go_into_state(message.from_user.id, "arrival")
    else:
        bot.send_message(message.from_user.id, "Неверный ввод!"
                                               " Нажмите на одну из кнопок меню.")


##### manual input #####
@bot.message_handler(func=lambda m: m.text == config.buttons['manual_input'])
def country_setting(message):
    current_state = changer.get_state(message.from_user.id)
    if redis.hexists(message.from_user.id, 'country'):
        if current_state == 'departure':
            state = "specify_departure_region"
        else:
            state = "specify_arrival_region"
        changer.specify_direction_region(message.from_user.id, state)
    else:
        if current_state == 'departure':
            state = "departure_input"
        else:
            state = "arrival_input"
        changer.direction_input(message.from_user.id, state)


#########################################
################ my_routes ##############

@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) == "my_routes")
def specify_radius(message):
    try:
        route_number = int(message.text)
    except ValueError:
        bot.send_message(message.from_user.id, 'Неверно указан номер маршрута!\nПопробуйте снова.')
    else:
        changer.specific_route(message.from_user.id, route_number=route_number)


#########################################
############## notifications ############

### NOTIFICATION LOGIC ###



#########################################
############### settings ################

@bot.message_handler(func=lambda m: m.text == config.buttons['change_country'] and
                     changer.get_state(m.from_user.id) == "settings")
def change_country(message):
    changer.go_into_state(message.from_user.id, "change_country")


@bot.callback_query_handler(func=lambda c: c.data in config.countries and
                            changer.get_state(c.from_user.id) == "change_country")
def new_country(c):
    handler.set_new_country(c.from_user.id, c.data)


#########################################
############ additional_info ############

@bot.message_handler(func=lambda m: m.text == config.buttons['about_bot'] and
                     changer.get_state(m.from_user.id) == "additional_info")
def bot_info(message):
    bot.send_message(message.from_user.id, config.additional_info['about_bot'],
                     disable_web_page_preview=True, parse_mode='markdown')


@bot.message_handler(func=lambda m: m.text == config.buttons['about_author'] and
                     changer.get_state(m.from_user.id) == "additional_info")
def author_info(message):
    bot.send_message(message.from_user.id, config.additional_info['about_author'])


##########################################
##########################################


@bot.message_handler(content_types=['location'])
def specify_radius(message):
    changer.geo_stations(message.from_user.id, message.location)

@bot.callback_query_handler(func=lambda c: c.data.startswith('gs'))
def inline(c):
    station_info = c.data[2:]
    station_code, station_title = station_info.split(maxsplit=1)
    if changer.get_state(c.from_user.id) == 'specify_radius_arr':
        redis.hset(c.from_user.id, 'arr_code', station_code)
        redis.hset(c.from_user.id, 'arr_station', station_title)
        state = 'sure_arr'
    else:
        redis.hset(c.from_user.id, 'dep_code', station_code)
        redis.hset(c.from_user.id, 'dep_station', station_title)
        state = 'sure_dep'
    changer.sure_station_geo(c.from_user.id, state, station_title)


@bot.message_handler(func=lambda m: m.text == config.buttons['geolocation'])
def geolocation(message):
    if changer.get_state(message.from_user.id) == 'departure':
        state = "specify_radius_dep"
    else:
        state = "specify_radius_arr"
    changer.specify_radius(message.from_user.id, state)


@bot.callback_query_handler(func=lambda c: c.data in ['-1', '+1',
                                                      '-5', '+5'])
def inline(c):
    changer.change_radius(int(c.data), c)

##########################################
##########################################
##########################################





@bot.callback_query_handler(func=lambda c: c.data in config.countries)
def set_country(c):
    country = c.data[3:]   # Удаляем флаг
    redis.hset(c.from_user.id, 'country', country)

    if changer.get_state(c.from_user.id) == "departure_input":
        state = "specify_departure_region"
    else:
        state = "specify_arrival_region"
    changer.specify_direction_region(c.from_user.id, state)





@bot.callback_query_handler(func=lambda c: len(c.data) == 1)
def first_letter_of_region(c):
    if changer.get_state(c.from_user.id) == 'specify_departure_region':
        state = "departure_region"
    else:
        state = "arrival_region"
    changer.direction_region(c.from_user.id, state, callback=c)


@bot.callback_query_handler(func=lambda c: c.data.startswith('R'))
def specify_region(c):
    if changer.get_state(c.from_user.id) == 'arrival_region':
        redis.hset(c.from_user.id, 'arr_region', c.data[1:])
        state = "specify_arrival_station"
    else:
        redis.hset(c.from_user.id, 'dep_region', c.data[1:])
        state = "specify_departure_station"
    changer.go_into_state(c.from_user.id, state)


@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) == "specify_arrival_station" or
                     changer.get_state(m.from_user.id) == "specify_departure_station")
def specify_station(message):
    station = message.text
    user_id = message.from_user.id
    state = changer.get_state(message.from_user.id)
    country = redis.get_str(user_id, 'country')

    if state == 'specify_arrival_station':
        region_title = redis.get_str(user_id, 'arr_region')
    else:
        region_title = redis.get_str(user_id, 'dep_region')
    requested_region = yandex_api.get_requested_region(region_title, country)
    stations = yandex_api.give_me_stations_by_name(station, requested_region)

    changer.check_values(user_id, state, stations)


@bot.callback_query_handler(func=lambda c: c.data.startswith('D'))
def inline(c):
    direction = c.data[1:]
    stations = json.loads(redis.get_str(c.from_user.id, 'stations'))
    for station in stations:
        if station['direction'] == direction:
            chosen_station = station
            break
    station_code = chosen_station['codes']['yandex_code']

    if changer.get_state(c.from_user.id) == 'specify_arrival_station':
        redis.hset(c.from_user.id, 'arr_station', chosen_station['title'])
        redis.hset(c.from_user.id, 'arr_code', station_code)
    else:
        redis.hset(c.from_user.id, 'dep_station', chosen_station['title'])
        latitude, longitude = chosen_station['latitude'], chosen_station['longitude']
        redis.hset(c.from_user.id, 'latitude', latitude)
        redis.hset(c.from_user.id, 'longitude', longitude)

    changer.sure_station(c.from_user.id, changer.get_state(c.from_user.id), chosen_station['title'])


@bot.callback_query_handler(func=lambda c: c.data == 'Изменить')
def inline(c):
    state = changer.get_state(c.from_user.id)
    if state == 'specify_radius_dep':
        changer.specify_radius(c.from_user.id, state)
    elif state == 'specify_radius_arr':
        changer.specify_radius(c.from_user.id, state)
    elif state == 'sure_arr':
        changer.go_into_state(c.from_user.id, 'departure')
    else:
        changer.go_into_state(c.from_user.id, 'arrival')


@bot.callback_query_handler(func=lambda c: c.data == 'Подтвердить')
def inline(c):
    if changer.both_stations_set(c.from_user.id):
        arr_station = redis.get_str(c.from_user.id, 'arr_station')
        dep_station = redis.get_str(c.from_user.id, 'dep_station')
        bot_response = "Задан маршрут *{0}* - *{1}*.".format(dep_station, arr_station)

        changer.create_route(c.from_user.id, bot_response)
    else:
        changer.go_into_state(c.from_user.id, 'new_route')


@bot.message_handler(func=lambda m: m.text == config.buttons['schedule'] and
                     changer.get_state(m.from_user.id) == "created_route")
def settings(message):
    changer.go_into_state(message.from_user.id, 'schedule')


@bot.message_handler(func=lambda m: m.text == config.buttons['nearest'] and
                     changer.get_state(m.from_user.id) == "schedule")
def settings(message):
    changer.go_into_state(message.from_user.id, 'nearest_schedule')


@bot.message_handler(func=lambda m: m.text == config.buttons['today'] and
                     changer.get_state(m.from_user.id) == "schedule")
def settings(message):
    changer.go_into_state(message.from_user.id, 'today_schedule')


@bot.message_handler(func=lambda m: m.text == config.buttons['tomorrow'] and
                     changer.get_state(m.from_user.id) == "schedule")
def settings(message):
    changer.go_into_state(message.from_user.id, 'tomorrow_schedule')


@bot.message_handler(func=lambda m: m.text == config.buttons['entire'] and
                     changer.get_state(m.from_user.id) == "schedule")
def settings(message):
    changer.go_into_state(message.from_user.id, 'entire_schedule')


@bot.message_handler(func=lambda m: m.text == config.buttons['set_notifications'] and
                     changer.get_state(m.from_user.id) in ['nearest_schedule',
                                                           'today_schedule',
                                                           'tomorrow_schedule',
                                                           'entire_schedule'])
def notify_me(message):
    changer.go_into_state(message.from_user.id, 'choose_electr')


@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) == "choose_electr")
def settings(message):
    try:
        electr_number = int(message.text)
    except ValueError:
        bot.send_message(message.from_user.id, 'Неверно указан номер маршрута!\nПопробуйте снова.')
    else:
        changer.notify_me(message.from_user.id, electr_number=electr_number)


@bot.callback_query_handler(func=lambda c: c.data == 'добавить')
def inline(c):
    route_key = 'routes:' + str(c.from_user.id)
    arr = redis.get_str(c.from_user.id, 'arr_station')
    dep = redis.get_str(c.from_user.id, 'dep_station')
    arr_code = redis.get_str(c.from_user.id, 'arr_code')
    dep_code = redis.get_str(c.from_user.id, 'dep_code')
    route = {'arr_station': arr, 'dep_station': dep, 'arr_code': arr_code, 'dep_code': dep_code}
    redis.rpush(route_key, json.dumps(route))




if __name__ == '__main__':
    bot.polling(none_stop=True)
