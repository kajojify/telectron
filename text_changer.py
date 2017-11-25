import config
import yandex_api
import json
import datetime

from notifications import get_current_datetime


class Text:
    def __init__(self, redis_storage):
        self.redis_storage = redis_storage

    def get_bot_text(self, user_id, state, response=None, **kwargs):
        if response is not None:
            text = response
        else:
            get_state_text = getattr(self, "{0}_text".format(state), None)
            if get_state_text is not None:
                text = get_state_text(user_id, **kwargs)
            else:
                text = config.permitted_states[state]['message']
        return text

    def main_menu_text(self, user_id, **kwargs):
        if self.redis_storage.hexists(user_id, 'routes'):
            new_response = config.permitted_states['main_menu']['message']['routes']
        else:
            new_response = config.permitted_states['main_menu']['message']['no_routes']
        return new_response

    def entire_schedule_text(self, user_id):
        arr = str(self.redis_storage.hget(user_id, 'arr_code'), 'utf-8')
        dep = str(self.redis_storage.hget(user_id, 'dep_code'), 'utf-8')
        full_schedule = yandex_api.output_full_schedule(dep, arr)
        return full_schedule

    def tomorrow_schedule_text(self, user_id):
        latitude = str(self.redis_storage.hget(user_id, 'latitude'), 'utf-8')
        longitude = str(self.redis_storage.hget(user_id, 'longitude'), 'utf-8')
        arr = str(self.redis_storage.hget(user_id, 'arr_code'), 'utf-8')
        dep = str(self.redis_storage.hget(user_id, 'dep_code'), 'utf-8')
        dep_datetime = get_current_datetime(latitude, longitude)
        dep_datetime += datetime.timedelta(days=1)
        print(dep_datetime)
        full_schedule = yandex_api.output_full_schedule(dep, arr, date=dep_datetime)
        return full_schedule

    def today_schedule_text(self, user_id):
        latitude = str(self.redis_storage.hget(user_id, 'latitude'), 'utf-8')
        longitude = str(self.redis_storage.hget(user_id, 'longitude'), 'utf-8')
        arr = str(self.redis_storage.hget(user_id, 'arr_code'), 'utf-8')
        dep = str(self.redis_storage.hget(user_id, 'dep_code'), 'utf-8')
        dep_datetime = get_current_datetime(latitude, longitude)
        full_schedule = yandex_api.nearest_full_schedule(dep, arr, date=dep_datetime)
        return full_schedule

    def nearest_schedule_text(self, user_id):
        latitude = str(self.redis_storage.hget(user_id, 'latitude'), 'utf-8')
        longitude = str(self.redis_storage.hget(user_id, 'longitude'), 'utf-8')
        arr = str(self.redis_storage.hget(user_id, 'arr_code'), 'utf-8')
        dep = str(self.redis_storage.hget(user_id, 'dep_code'), 'utf-8')
        dep_datetime = get_current_datetime(latitude, longitude)
        full_schedule = yandex_api.nearest_full_schedule(dep, arr, date=dep_datetime)
        return full_schedule


    def my_routes_text(self, user_id, **kwargs):
        route_key = 'routes:' + str(user_id)
        routes_number = self.redis_storage.llen(route_key)
        all_routes = self.redis_storage.lrange(route_key, 0, routes_number-1)
        print(all_routes)
        if not all_routes:
            text = "Вы пока добавили ни единого маршрута!"
        else:
            text = ''
            for i, route in enumerate(all_routes, 1):
                route_dump = str(route, 'utf-8')
                route_json = json.loads(route_dump)
                route_str = "*{0}.* {1} - {2}\n".format(i, route_json['dep_station'], route_json['arr_station'])
                text += route_str
        return text

    def specific_route_text(self, user_id, **kwargs):
        route_number = kwargs['route_number']
        route_key = 'routes:' + str(user_id)
        route = str(self.redis_storage.lrange(route_key, route_number-1, route_number-1)[0], 'utf-8')
        route_json = json.loads(route)
        return yandex_api.output_full_schedule(route_json['dep_code'], route_json['arr_code'])
