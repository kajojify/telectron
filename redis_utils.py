import json

import redis
from telebot import types

import config
import yandex_api
from keyboard import Keyboard
from text_changer import Text


class Redis:
    def __init__(self):
        self.storage = redis.StrictRedis()

    def get_str(self, user_id, key):
        return str(self.storage.hget(user_id, key), 'utf-8')

    def __getattr__(self, item):
        return getattr(self.storage, item)


class StateChanger:
    def __init__(self, bot, redis_storage):
        self.bot = bot
        self.redis = redis_storage
        self.geo_radius = 5
        self.keyboard = Keyboard()
        self.text = Text(self.redis)

    def get_state(self, user_id):
        return self.redis.get_str(user_id, "state")

    def set_state(self, user_id, state):
        if state in config.permitted_states:
            self.redis.hset(str(user_id), "state", state)
        else:
            raise ValueError("There is no such state")

    def go_into_state(self, user_id, state, arbitrary_response=None):
        """
        Standard state changer
        """
        self.set_state(user_id, state)

        text = self.text.get_bot_text(user_id, state, arbitrary_response)

        keyboard = self.keyboard.get_state_keyboard(state)
        self.bot.send_message(user_id, text, reply_markup=keyboard,
                              parse_mode='markdown')

    #######################
    #######################
    #######################
    #######################
    # Custom state changers

    def already_set_direction(self, user_id, state):
        self.set_state(user_id, state)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Всё равно продолжить',
                                                callback_data='Всё равно продолжить'))

        if state == 'already_set_departure':
            station_name = self.redis.get_str(user_id, 'dep_station')
        else:
            station_name = self.redis.get_str(user_id, 'arr_station')
        text = config.permitted_states[state]['message'].format(station_name)
        self.bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="markdown")

    def specify_radius(self, user_id, state):
        self.set_state(user_id, state)
        comeback = self.keyboard.geostations()
        keyboard = self.keyboard.specify_radius()

        responses = config.permitted_states[state]['message']
        self.bot.send_message(user_id, responses[0], reply_markup=comeback,
                              parse_mode="markdown")
        self.bot.send_message(user_id, responses[1], reply_markup=keyboard,
                              parse_mode="markdown")


    def direction_input(self, user_id, state):
        self.set_state(user_id, state)

        comeback = self.keyboard.get_additional_comeback_keyboard()
        keyboard = self.keyboard.direction_input(state)

        responses = config.permitted_states[state]['message']
        self.bot.send_message(user_id, responses[0], reply_markup=comeback,
                              parse_mode='markdown')
        self.bot.send_message(user_id, responses[1], reply_markup=keyboard)

    def specify_direction_region(self, user_id, state):
        self.set_state(user_id, state)

        country = self.redis.get_str(user_id, 'country')
        country_string = "Страна: *{0}*\n".format(country)
        regions_alphabet = yandex_api.get_regions_alphabet(country)

        comeback = self.keyboard.get_additional_comeback_keyboard()
        keyboard = self.keyboard.specify_direction_region(regions_alphabet)

        responses = config.permitted_states[state]['message']
        self.bot.send_message(user_id, country_string + responses[0],
                              reply_markup=comeback, parse_mode='markdown')
        self.bot.send_message(user_id, responses[1], reply_markup=keyboard)

    def direction_region(self, user_id, state, callback):
        self.set_state(user_id, state)
        country = self.redis.get_str(user_id, 'country')
        desired_regions = yandex_api.give_me_regions_by_letter(callback.data, country)

        keyboard = self.keyboard.direction_region(desired_regions)

        self.bot.edit_message_reply_markup(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            inline_message_id=callback.inline_message_id,
            reply_markup=keyboard)

    def check_values(self, user_id, state, stations):
        self.set_state(user_id, state)

        if len(stations) == 0:
            self.bot.send_message(user_id, 'К сожалению, станция не найдена! Попробуйте снова.')

        elif len(stations) == 1:
            chosen_station = stations[0]
            station_code = chosen_station['codes']['yandex_code']
            if self.get_state(user_id) == 'specify_arrival_station':
                self.redis.hset(user_id, 'arr_station', chosen_station['title'])
                self.redis.hset(user_id, 'arr_code', station_code)
            else:
                self.redis.hset(user_id, 'dep_station', chosen_station['title'])
                self.redis.hset(user_id, 'dep_code', station_code)
                latitude, longitude = chosen_station['latitude'], chosen_station['longitude']
                self.redis.hset(user_id, 'latitude', latitude)
                self.redis.hset(user_id, 'longitude', longitude)
            self.sure_station(user_id, state, chosen_station['title'])
        else:
            self.clarify_direction(user_id, stations)

    def both_stations_set(self, user_id):
        if self.redis.hexists(user_id, 'arr_code') and self.redis.hexists(user_id, 'dep_code'):
            return True
        else:
            return False

    def clarify_direction(self, user_id, stations):
        self.redis.hset(user_id, 'stations', json.dumps(stations))
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=station['direction'],
                                                  callback_data='D'+station['direction'])
                           for station in stations])
        self.bot.send_message(user_id, 'Выберете железнодорожную ветку вашей станции!', reply_markup=keyboard)

    def change_radius(self, r_diff, c):
        if self.geo_radius == 1 and r_diff < 0 or self.geo_radius == 20 and r_diff > 0:
            return
        self.geo_radius += r_diff
        if self.geo_radius < 1:
            self.geo_radius = 1
        elif self.geo_radius > 20:
            self.geo_radius = 20

        keyboard = self.keyboard.specify_radius()
        self.bot.edit_message_text(message_id=c.message.message_id,
                                   chat_id=c.message.chat.id,
                                   inline_message_id=c.inline_message_id,
                                   text='Радиус поиска   -  *%d км*' % self.geo_radius,
                                   reply_markup=keyboard,
                                   parse_mode='markdown')


    def geo_stations(self, user_id, location):
        latitude = location.latitude
        longitude = location.longitude
        nearest_stations = yandex_api.get_nearest_stations(latitude,
                                                           longitude, self.geo_radius)

        stations = nearest_stations['stations']
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*[types.InlineKeyboardButton(text=station['title'], callback_data='gs'+station['code']+ ' ' + station['title'])
                       for station in stations])
        self.bot.send_message(user_id, 'В радиусе %d км найдены такие станции:' % self.geo_radius, reply_markup=keyboard)

    def sure_station_geo(self, user_id, state, station_title):
        print(state)
        self.set_state(user_id, state)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Изменить', callback_data='Изменить'))
        keyboard.add(types.InlineKeyboardButton(text='Подтвердить', callback_data='Подтвердить'))

        direction = 'отправления' if state == 'sure_dep' else 'прибытия'
        station_confirmation = "Ваша станция {0}:\n" \
                               "*регион {0}*: согласно геопозиции\n" \
                               "*станция {0}*: {1}".format(direction, station_title)
        self.bot.send_message(user_id, station_confirmation, reply_markup=keyboard, parse_mode="markdown")

    def sure_station(self, user_id, state, station_title):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Изменить', callback_data='Изменить'))
        keyboard.add(types.InlineKeyboardButton(text='Подтвердить', callback_data='Подтвердить'))

        if state == 'specify_departure_station':
            region = self.redis.get_str(user_id, 'dep_region')
            direction = 'отправления'
        else:
            direction = 'прибытия'
            region = self.redis.get_str(user_id, 'arr_region')

        station_confirmation = "Ваша станция {0}:\n" \
                               "*регион {0}*: {1}\n" \
                               "*станция {0}*: {2}".format(direction, region, station_title)
        self.bot.send_message(user_id, station_confirmation, reply_markup=keyboard, parse_mode="markdown")

    def create_route(self, user_id, bot_response):
        state = 'created_route'
        self.set_state(user_id, state)
        ad_keyboard = types.InlineKeyboardMarkup()
        ad_keyboard.add(types.InlineKeyboardButton(text='Добавить в Мои маршруты',
                                                callback_data='добавить'))

        keyboard = self.keyboard.create_route(state)
        self.bot.send_message(user_id, bot_response, reply_markup=ad_keyboard,
                              parse_mode='markdown')
        self.bot.send_message(user_id, 'Что Вас интересует?', reply_markup=keyboard,
                              parse_mode='markdown')

    def specific_route(self, user_id, route_number):
        state = 'specific_route'
        self.set_state(user_id, state)
        text = self.text.get_bot_text(user_id, state, route_number=route_number)

        keyboard = self.keyboard.get_state_keyboard(state)
        self.bot.send_message(user_id, text, reply_markup=keyboard,
                              parse_mode='markdown')

    def notify_me(self, user_id, electr_number):
        state = 'notify_me'
        self.set_state(user_id, state)
        text = self.text.get_bot_text(user_id, state, electr_number=electr_number)

        keyboard = self.keyboard.get_state_keyboard(state)
        self.bot.send_message(user_id, text, reply_markup=keyboard,
                              parse_mode='markdown')


class DataHandler:
    def __init__(self, bot, redis_storage):
        self.bot = bot
        self.redis = redis_storage

    def set_new_value(self, callback, key):
        pass

    def set_new_country(self, user_id, country):
        new_country = country[3:]  # Delete a flag
        self.redis.hset(user_id, "country", new_country)
        self.bot.send_message(user_id, "Страна изменена."
                              " Ваша текущая страна - {}".format(config))


