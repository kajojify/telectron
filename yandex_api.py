import json
import requests
from datetime import datetime

from config import country_numbers, yandex_apikey


def load_stations_data(json_file):
    with open(json_file) as jf:
        return json.load(jf)


def get_regions(country, json_file="stations.json"):
    yandex_stations = load_stations_data(json_file)
    country_index = country_numbers[country]
    country_regions = yandex_stations['countries'][country_index]['regions']
    return country_regions


def get_regions_alphabet(country):
    regions = get_regions(country)
    first_letters = set()
    for region in regions:
        if region['title']:
            first_letters.add(region['title'][0])
    regions_first_letters = list(first_letters)
    regions_first_letters.sort()
    return "".join(regions_first_letters)


def give_me_regions_by_letter(letter, country):
    regions = get_regions(country)
    desired_list = []
    for region in regions:
        region_title = region['title']
        if region_title and region_title[0] == letter:
            desired_list.append(region)
    return desired_list


def get_requested_region(region_title, country):
    regions = get_regions(country)
    for region in regions:
        if region_title == region['title']:
            return region


def give_me_stations_by_name(station_title, region):
    stations_list = []
    for settlement in region['settlements']:
        for station in settlement['stations']:
            if station['title'] == station_title:
                stations_list.append(station)
    return stations_list


def output_full_schedule(dep_st_code, arr_st_code, date=None):
    full_schedule_str = ""
    query = {'apikey': yandex_apikey, 'from': dep_st_code, 'to': arr_st_code,
             'transport_types': 'suburban'}
    if not isinstance(date, datetime):
        raise TypeError('Аргумент date должен быть объектом класса datetime.datetime!')
    if date is not None:
        query['date'] = date.strftime("%Y-%m-%d")
    full_schedule_json = requests.get("https://api.rasp.yandex.net/v3.0/search/", params=query).json()
    dep = full_schedule_json['search']['from']['title']
    arr = full_schedule_json['search']['to']['title']
    all_subtrains = full_schedule_json['segments']
    for subtrain in all_subtrains:
        departure_time = subtrain['departure'][:-6].split('T')[1]
        # except_days = subtrain['except_days']
        arrival_time = subtrain['arrival'][:-6].split('T')[1]
        from_station = subtrain['from']['title']
        to_station = subtrain['to']['title']
        # days = subtrain['days']
        title = subtrain['thread']['title']
        duration = subtrain['duration']
        stops = subtrain['stops']
        # when = '\n*Когда:* {0}'.format(days) + (', кроме {0}.\n\n'.format(except_days) if except_days else '.\n\n')
        subtrain_str = "\n*Следование:* {0}\n {1}     {2}\n{3}  -  {4}\n".format(title, dep, arr, departure_time, arrival_time)
        # subtrain_str += when
        full_schedule_str += subtrain_str
    return full_schedule_str

def nearest_full_schedule(dep_st_code, arr_st_code, date):
    full_schedule_str = ""
    if not isinstance(date, datetime):
        raise TypeError('Аргумент date должен быть объектом класса datetime.datetime!')
    query = {'apikey': yandex_apikey, 'from': dep_st_code, 'to': arr_st_code,
             'transport_types': 'suburban', 'date': date.strftime("%Y-%m-%d")}

    full_schedule_json = requests.get("https://api.rasp.yandex.net/v3.0/search/", params=query).json()
    dep = full_schedule_json['search']['from']['title']
    arr = full_schedule_json['search']['to']['title']
    all_subtrains = full_schedule_json['segments']
    for subtrain in all_subtrains:
        departure_time = datetime.strptime(subtrain['departure'][:-6], "%Y-%m-%dT%H:%M:%S")
        if date > departure_time:
            continue

        departure_time = subtrain['departure'][:-6].split('T')[1]
        arrival_time = subtrain['arrival'][:-6].split('T')[1]

        title = subtrain['thread']['title']

        subtrain_str = "\n*Следование:* {0}\n {1}     {2}\n{3}  -  {4}\n".format(title, dep, arr, departure_time, arrival_time)
        full_schedule_str += subtrain_str
    return full_schedule_str if full_schedule_str else 'Все уехали :)'


def get_nearest_stations(latitude, longitude, radius):
    query = {'apikey': yandex_apikey, 'lat': latitude, 'lng': longitude,
             'transport_types': 'train,suburban', 'distance': radius}
    nearest_stations = requests.get("https://api.rasp.yandex.net/v3.0/nearest_stations/", params=query).json()
    return nearest_stations
