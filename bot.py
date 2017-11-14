import json

import telebot

import config
import yandex_api
from redis_utils import StateChanger

bot = telebot.TeleBot(config.bot_token)
changer = StateChanger(bot)


#########################################
############### main_menu ###############

@bot.message_handler(commands=['start'])
def start(message):
    changer.go_into_state(message.from_user.id, 'main_menu')


@bot.message_handler(func=lambda m: m.text == config.buttons['new_route'] and
                     changer.get_state(m.from_user.id) == "main_menu")
def new_route(message):
    changer.go_into_state(message.from_user.id, 'new_route')


@bot.message_handler(func=lambda m: m.text == config.buttons['my_routes'] and
                     changer.get_state(m.from_user.id) == "main_menu")
def my_routes(message):
    changer.go_into_state(message.from_user.id, 'my_routes')


#########################################
############ settings ############

@bot.message_handler(func=lambda m: m.text == config.buttons['settings'] and
                     changer.get_state(m.from_user.id) == "main_menu")
def settings(message):
    changer.go_into_state(message.from_user.id, 'settings')


@bot.message_handler(func=lambda m: m.text == config.buttons['change_country'] and
                     changer.get_state(m.from_user.id) == "settings")
def settings(message):
    changer.go_into_state(message.from_user.id, 'change_country')


@bot.callback_query_handler(func=lambda c: c.data in config.countries and
                            changer.get_state(c.from_user.id) == "settings")
def change_country(c):
    country = c.data[3:]  # Удаляем флаг
    changer.redis_storage.hset(c.from_user.id, 'country', country)
    bot.send_message(c.from_user.id, 'Страна изменена.')

#########################################
############ additional_info ############

@bot.message_handler(func=lambda m: m.text == config.buttons['additional_info'] and
                     changer.get_state(m.from_user.id) == "main_menu")
def additional_info(message):
    changer.go_into_state(message.from_user.id, 'additional_info')


@bot.message_handler(func=lambda m: m.text == config.buttons['about_bot'] and
                     changer.get_state(m.from_user.id) == "additional_info")
def settings(message):
    bot.send_message(message.from_user.id, config.additional_info['about_bot'],
                     disable_web_page_preview=True, parse_mode='markdown')


@bot.message_handler(func=lambda m: m.text == config.buttons['about_author'] and
                     changer.get_state(m.from_user.id) == "additional_info")
def settings(message):
    bot.send_message(message.from_user.id, config.additional_info['about_author'])

#########################################
#########################################


@bot.message_handler(func=lambda m: m.text == config.buttons['comeback'] and
                     changer.get_state(m.from_user.id) in config.comeback_button)
def comeback(message):
    state = changer.get_state(message.from_user.id)
    comebacking_state = config.comeback_button[state]

    changer.go_into_state(message.from_user.id, comebacking_state)


@bot.message_handler(func=lambda m: (m.text == config.buttons['departure'] or
                     m.text == config.buttons['arrival']) and
                     (changer.get_state(m.from_user.id) in ["new_route",
                                                            "already_set_departure",
                                                            "already_set_arrival"]))
def station_specifying(message):
    if message.text == config.buttons['departure']:
        if changer.redis_storage.hexists(message.from_user.id, 'dep_code'):
            changer.already_set_direction(message.from_user.id, "already_set_departure")
        else:
            changer.go_into_state(message.from_user.id, 'departure')
    else:
        if changer.redis_storage.hexists(message.from_user.id, 'arr_code'):
            changer.already_set_direction(message.from_user.id, "already_set_arrival")
        else:
            changer.go_into_state(message.from_user.id, 'arrival')


@bot.callback_query_handler(func=lambda c: (c.data == 'Всё равно продолжить' and
                                    (changer.get_state(c.from_user.id) == "already_set_departure" or
                                     changer.get_state(c.from_user.id) == "already_set_arrival")))
def station_specifying(c):
    if changer.get_state(c.from_user.id) == "already_set_departure":
        state = "departure"
    else:
        state = "arrival"
    changer.go_into_state(c.from_user.id, state)

##########################################
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
        changer.redis_storage.hset(c.from_user.id, 'arr_code', station_code)
        changer.redis_storage.hset(c.from_user.id, 'arr_station', station_title)
        state = 'sure_arr'
    else:
        changer.redis_storage.hset(c.from_user.id, 'dep_code', station_code)
        changer.redis_storage.hset(c.from_user.id, 'dep_station', station_title)
        state = 'sure_dep'
    changer.sure_station_geo(c.from_user.id, state, station_title)


@bot.message_handler(func=lambda m: m.text == config.buttons['geolocation'] and
                     (changer.get_state(m.from_user.id) == 'departure' or
                      changer.get_state(m.from_user.id) == 'arrival'))
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


@bot.message_handler(func=lambda m: m.text == config.buttons['manual_input'] and
                     (changer.get_state(m.from_user.id) == 'departure' or
                      changer.get_state(m.from_user.id) == 'arrival') and
                      not changer.redis_storage.hexists(m.from_user.id, 'country'))
def manual_input_without_country(message):
    if changer.get_state(message.from_user.id) == 'departure':
        state = "departure_input"
    else:
        state = "arrival_input"
    changer.direction_input(message.from_user.id, state)


@bot.callback_query_handler(func=lambda c: c.data in config.countries and
                            (changer.get_state(c.from_user.id) == "departure_input" or
                             changer.get_state(c.from_user.id) == "arrival_input"))
def set_country(c):
    country = c.data[3:]   # Удаляем флаг
    changer.redis_storage.hset(c.from_user.id, 'country', country)

    if changer.get_state(c.from_user.id) == "departure_input":
        state = "specify_departure_region"
    else:
        state = "specify_arrival_region"
    changer.specify_direction_region(c.from_user.id, state)


@bot.message_handler(func=lambda m: m.text == config.buttons['manual_input'] and
                     (changer.get_state(m.from_user.id) == 'departure' or
                      changer.get_state(m.from_user.id) == 'arrival') and
                      changer.redis_storage.hexists(m.from_user.id, 'country'))
def manual_input_with_country(message):
    if changer.get_state(message.from_user.id) == 'departure':
        state = "specify_departure_region"
    else:
        state = "specify_arrival_region"

    changer.specify_direction_region(message.from_user.id, state)


@bot.callback_query_handler(func=lambda c: len(c.data) == 1 and
                            (changer.get_state(c.from_user.id) == 'specify_departure_region' or
                             changer.get_state(c.from_user.id) == 'specify_arrival_region'))
def first_letter_of_region(c):
    if changer.get_state(c.from_user.id) == 'specify_departure_region':
        state = "departure_region"
    else:
        state = "arrival_region"
    changer.direction_region(c.from_user.id, state, callback=c)


@bot.callback_query_handler(func=lambda c: c.data.startswith('R'))
def specify_region(c):
    if changer.get_state(c.from_user.id) == 'arrival_region':
        changer.redis_storage.hset(c.from_user.id, 'arr_region', c.data[1:])
        state = "specify_arrival_station"
    else:
        changer.redis_storage.hset(c.from_user.id, 'dep_region', c.data[1:])
        state = "specify_departure_station"
    changer.go_into_state(c.from_user.id, state)


@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) == "specify_arrival_station" or
                     changer.get_state(m.from_user.id) == "specify_departure_station")
def specify_station(message):
    station = message.text
    user_id = message.from_user.id
    state = changer.get_state(message.from_user.id)
    country = str(changer.redis_storage.hget(user_id, 'country'), 'utf-8')

    if state == 'specify_arrival_station':
        region_title = str(changer.redis_storage.hget(user_id, 'arr_region'), 'utf-8')
    else:
        region_title = str(changer.redis_storage.hget(user_id, 'dep_region'), 'utf-8')
    requested_region = yandex_api.get_requested_region(region_title, country)
    stations = yandex_api.give_me_stations_by_name(station, requested_region)

    changer.check_values(user_id, state, stations)


@bot.callback_query_handler(func=lambda c: c.data.startswith('D'))
def inline(c):
    direction = c.data[1:]
    stations = json.loads(str(changer.redis_storage.hget(c.from_user.id, 'stations'), 'utf-8'))
    for station in stations:
        if station['direction'] == direction:
            chosen_station = station
            break
    station_code = chosen_station['codes']['yandex_code']
    if changer.get_state(c.from_user.id) == 'specify_arrival_station':
        changer.redis_storage.hset(c.from_user.id, 'arr_station', chosen_station['title'])
        changer.redis_storage.hset(c.from_user.id, 'arr_code', station_code)
    else:
        changer.redis_storage.hset(c.from_user.id, 'dep_station', chosen_station['title'])
        changer.redis_storage.hset(c.from_user.id, 'dep_code', station_code)

    if changer.both_stations_set(c.from_user.id):
        changer.are_you_sure(c.from_user.id)
    else:
        changer.go_into_state(c.from_user.id, 'new_route')


@bot.callback_query_handler(func=lambda c: c.data == 'Изменить')
def inline(c):
    bot.send_message(c.from_user.id, "Ведутся работы!")

@bot.callback_query_handler(func=lambda c: c.data == 'Подтвердить')
def inline(c):
    if changer.both_stations_set(c.from_user.id):
        changer.set_state(c.from_user.id, 'choose_subtrain')
        arrcode = str(changer.redis_storage.hget(c.from_user.id, 'arr_code'), 'utf-8')
        depcode = str(changer.redis_storage.hget(c.from_user.id, 'dep_code'), 'utf-8')
        schedule = yandex_api.get_full_schedule(depcode, arrcode)
        full_schedule_str = ''
        for i, subtrain in enumerate(schedule, 1):
            departure = subtrain['departure']
            title = subtrain['thread']['title']
            # except_days = subtrain['except_days']
            arrival = subtrain['arrival']
            duration = subtrain['duration']
            stops = subtrain['stops']
            # days = subtrain['days']
            subtrain_str = "{0}. {1} ---  {2}  -  {3}.\n\n".format(i, title, departure, arrival)
            full_schedule_str += subtrain_str
        changer.redis_storage.hset(c.from_user.id, 'schedule', json.dumps(schedule))
        dep_station = str(changer.redis_storage.hget(c.from_user.id, 'dep_station'), 'utf-8')
        arr_station = str(changer.redis_storage.hget(c.from_user.id, 'arr_station'), 'utf-8')
        changer.redis_storage.hdel(c.from_user.id, 'arr_code', 'dep_code')
        bot.send_message(c.from_user.id, 'Поехали! {} -- {}. \n\n{}'.format(dep_station,
                                                                            arr_station, full_schedule_str),
                         parse_mode='markdown')

    else:
        if changer.get_state(c.from_user.id) == 'sure_dep':
            new_response = "А теперь укажите *станция отправления*."
            changer.go_into_state(c.from_user.id, 'new_route', arbitrary_response=new_response)
        elif changer.get_state(c.from_user.id) == 'sure_arr':
            new_response = "А теперь укажите *станция прибытия*."
            changer.go_into_state(c.from_user.id, 'new_route', arbitrary_response=new_response)
        elif changer.get_state(c.from_user.id) == 'specify_departure_station':
            new_response = "А теперь укажите *станцию прибытия*."
            changer.go_into_state(c.from_user.id, 'new_route', arbitrary_response=new_response)
        else:
            new_response = "А теперь укажите *станцию отправления*."
            changer.go_into_state(c.from_user.id, 'new_route', arbitrary_response=new_response)
    # user_id = c.from_user.id
    # changer.set_state(user_id, "print_schedule")
    # arrcode = str(changer.redis_storage.hget(user_id, 'arr_code'), 'utf-8')
    # depcode = str(changer.redis_storage.hget(user_id, 'dep_code'), 'utf-8')
    # country = str(changer.redis_storage.hget(user_id, 'country'), 'utf-8')
    # dep_region = str(changer.redis_storage.hget(user_id, 'dep_region'), 'utf-8')
    # arr_region = str(changer.redis_storage.hget(user_id, 'arr_region'), 'utf-8')
    # dep_station = str(changer.redis_storage.hget(user_id, 'dep_station'), 'utf-8')
    # arr_station = str(changer.redis_storage.hget(user_id, 'arr_station'), 'utf-8')
    #
    # schedule = yandex_api.get_full_schedule(depcode, arrcode)
    # changer.redis_storage.hset(user_id, 'full_schedule', schedule)
    # bot.send_message(user_id, schedule)

@bot.message_handler(func=lambda m: changer.get_state(m.from_user.id) == 'choose_subtrain')
def specify_station(message):
    try:
        subtrain_number = int(message.text)
    except ValueError:
        bot.send_message(message.from_user.id, 'Неверно указан номер электрички!\nПопробуйте снова.')
    else:
        schedule = json.loads(str(changer.redis_storage.hget(message.from_user.id, 'schedule'), 'utf-8'))
        bot.send_message(message.from_user.id, json.dumps(schedule[subtrain_number]))

if __name__ == '__main__':
    bot.polling(none_stop=True)
