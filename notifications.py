import requests
from datetime import datetime

from config import google_apikey


def get_current_datetime(latitude, longitude):
    url = "https://maps.googleapis.com/maps/api/timezone/json"
    coordinates = "{0},{1}".format(latitude, longitude)
    timestamp = datetime.utcnow().timestamp()

    query = {'key': google_apikey, 'location': coordinates,
             'timestamp': timestamp}
    data = requests.get(url, params=query, timeout=1).json()

    raw_offset, dst_offset = data['rawOffset'], data['dstOffset']
    new_time = timestamp + raw_offset + dst_offset
    return datetime.fromtimestamp(new_time)
