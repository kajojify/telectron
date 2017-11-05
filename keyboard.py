import config

from telebot import types


class Keyboard:
    def get_state_keyboard(self, state):
        if config.permitted_states[state]['keyboard'] == 'reply':
            keyboard = self.get_standard_replykeyboard(state)
        elif config.permitted_states[state]['keyboard'] == 'inline':
            keyboard = self.get_standard_inlinekeyboard(state)
        else:
            keyboard = None
        return keyboard

    def get_standard_replykeyboard(self, state):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(*config.permitted_states[state]['buttons'])
        return keyboard

    def get_standard_inlinekeyboard(self, state):
        keyboard = types.InlineKeyboardMarkup()
        buttons = config.permitted_states[state]['buttons']
        keyboard.add(*[types.InlineKeyboardButton(text=button, callback_data=button)
                       for button in buttons])
        return keyboard

    def get_additional_comeback_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(config.buttons['comeback'])
        return keyboard

    ##################
    ##################
    ##################
    ##################
    # Custom keyboards

    def geostations(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(types.KeyboardButton(config.buttons['send_geolocation'],
                                          request_location=True))
        keyboard.row(config.buttons['comeback'])
        return keyboard

    def specify_radius(self):
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        keyboard.row(*[types.InlineKeyboardButton(text=number + ' км', callback_data=number)
                       for number in ['-1', '-5', '+1', '+5']])
        return keyboard

    def specify_direction_region(self, buttons):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=letter, callback_data=letter)
                       for letter in buttons])
        return keyboard

    def direction_region(self, buttons):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=region['title'], callback_data="R" + region['title'])
                       for region in buttons])
        return keyboard
