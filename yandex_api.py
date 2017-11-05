import json
import requests

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


def get_station_code(station, regions):
    for r in regions:
        for s in r['settlements']:
            for st in s['stations']:
                if st['title'] == station:
                    return st['codes']['yandex_code']


def get_full_schedule(dep_st_code, arr_st_code):
    full_schedule_str = ""
    query = {'apikey': yandex_apikey, 'from': dep_st_code, 'to': arr_st_code,
             'transport_types': 'suburban'}
    full_schedule_json = requests.get("https://api.rasp.yandex.net/v3.0/search/", params=query).json()
    all_subtrains = full_schedule_json['segments']
    for i, subtrain in enumerate(all_subtrains, 1):
        departure = subtrain['departure']
        title = subtrain['thread']['title']
        # except_days = subtrain['except_days']
        arrival = subtrain['arrival']
        duration = subtrain['duration']
        stops = subtrain['stops']
        # days = subtrain['days']
        subtrain_str = "{0}. {1} ---  {2}  -  {3}.\n\n".format(i, title, departure, arrival)
        # if except_days:
        #     subtrain_str += "\nКроме дней: {}\n\n".format(except_days)
        # else:
        #     subtrain_str += "\n\n"
        full_schedule_str += subtrain_str
    return full_schedule_str


def get_nearest_stations(latitude, longitude, radius):
    query = {'apikey': yandex_apikey, 'lat': latitude, 'lng': longitude,
             'transport_types': 'train,suburban', 'distance': radius}
    nearest_stations = requests.get("https://api.rasp.yandex.net/v3.0/nearest_stations/", params=query).json()
    return nearest_stations
