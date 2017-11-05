import redis
from telebot import types

import config
import yandex_api
from keyboard import Keyboard


class StateChanger:
    def __init__(self, bot):
        self.bot = bot
        self.geo_radius = 5
        self.keyboard = Keyboard()
        self.redis_storage = redis.StrictRedis()

    def get_state(self, user_id):
        return str(self.redis_storage.hget(user_id, 'state'), 'utf-8')

    def set_state(self, user_id, state):
        if state in config.permitted_states:
            self.redis_storage.hset(str(user_id), 'state', state)
        else:
            raise ValueError

    def go_into_state(self, user_id, state, arbitrary_response=None, **kwargs):
        self.set_state(user_id, state)

        text = self.get_bot_response(state, arbitrary_response)

        keyboard = self.keyboard.get_state_keyboard(state)
        self.bot.send_message(user_id, text, reply_markup=keyboard,
                              parse_mode='markdown', **kwargs)

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

        text = config.permitted_states[state]['message']
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
        keyboard = self.keyboard.get_state_keyboard(state)

        responses = config.permitted_states[state]['message']
        self.bot.send_message(user_id, responses[0], reply_markup=comeback)
        self.bot.send_message(user_id, responses[1], reply_markup=keyboard)

    def specify_direction_region(self, user_id, state):
        self.set_state(user_id, state)

        country = str(self.redis_storage.hget(user_id, 'country'), 'utf-8')
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
        country = str(self.redis_storage.hget(user_id, 'country'), 'utf-8')
        desired_regions = yandex_api.give_me_regions_by_letter(callback.data, country)

        keyboard = self.keyboard.direction_region(desired_regions)

        self.bot.edit_message_reply_markup(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            inline_message_id=callback.inline_message_id,
            reply_markup=keyboard)

    def check_values(self, user_id, state, **kwargs):
        self.set_state(user_id, state)
        stations = kwargs['stations']

        responses = config.permitted_states[state]['message']

        if len(stations) == 0:
            self.bot.send_message(user_id, responses[0])

        elif len(stations) == 1:
            chosen_station = stations[0]
            station_code = chosen_station['codes']['yandex_code']
            if self.get_state(user_id) == 'specify_arrival_station':
                self.redis_storage.hset(user_id, 'arr_station', chosen_station['title'])
                self.redis_storage.hset(user_id, 'arr_code', station_code)
            else:
                self.redis_storage.hset(user_id, 'dep_station', chosen_station['title'])
                self.redis_storage.hset(user_id, 'dep_code', station_code)
            if self.both_stations_set(user_id):
                self.are_you_sure(user_id)
            else:
                self.go_into_state(user_id, 'new_route')
        else:
            self.clarify_direction(user_id, state, stations=stations)

    def both_stations_set(self, user_id):
        if self.redis_storage.hexists(user_id, 'arr_code') and self.redis_storage.hexists(user_id, 'dep_code'):
            return True
        else:
            return False

    def are_you_sure(self, user_id):

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Изменить', callback_data='Изменить'))
        keyboard.add(types.InlineKeyboardButton(text='Подтвердить', callback_data='Подтвердить'))

        inputt = """Проверьте введённые данные:
                        *страна: *{0}
                        *регион отправки: *{1}
                        *станция отправки: *{2}
                        *регион прибытия: *{3}
                        *станция прибытия: *{4}
        """.format(str(self.redis_storage.hget(user_id, 'country'), 'utf-8'),
                    str(self.redis_storage.hget(user_id, 'dep_region'), 'utf-8'),
                    str(self.redis_storage.hget(user_id, 'dep_station'), 'utf-8'),
                    str(self.redis_storage.hget(user_id, 'arr_region'), 'utf-8'),
                    str(self.redis_storage.hget(user_id, 'arr_station'), 'utf-8'))
        self.bot.send_message(user_id, inputt, reply_markup=keyboard, parse_mode="markdown")


    def clarify_direction(self, user_id, state, stations):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=station['direction'],
                                                  callback_data=station['direction'])
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
        keyboard.add(*[types.InlineKeyboardButton(text=station['title'], callback_data=station['code'])
                       for station in stations])
        self.bot.send_message(user_id, 'В радиусе %d км найдены такие станции:' % self.geo_radius, reply_markup=keyboard)

    @staticmethod
    def get_bot_response(state, response):
        if response:
            text = response
        else:
            text = config.permitted_states[state]['message']
        return text
