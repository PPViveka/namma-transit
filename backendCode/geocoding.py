import os

import requests
from urllib.parse import urlencode
from pprint import pprint
from decouple import config

# api_key = os.environ.get("API_KEY")  # Get API Key From Your Device "System Environment Variable"
api_key = config('KEY2')


def geocoding_from_address(address):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address + ", Bengaluru, Karnataka, India", 'region': 'in', "key": api_key}
    url_params = urlencode(params)

    url = f"{endpoint}?{url_params}"
    req = requests.get(url)
    results = req.json().get('results', [])
    if not results:
        # Fallback: return Bengaluru city centre if geocoding fails
        return {
            'formatted_address': address + ', Bengaluru',
            'lat': 12.9716,
            'lng': 77.5946,
        }
    formatted_address = results[0]['formatted_address']
    lat = results[0]['geometry']['location']['lat']
    lng = results[0]['geometry']['location']['lng']
    data = {
        'formatted_address': formatted_address,
        'lat': lat,
        'lng': lng
    }
    return data


# p = geocoding_from_address('Jhigatola bust stop')
# print(p)

def reverse_geocoding(latlang):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json"
    url = f"{endpoint}?latlng={latlang}&region=in&key={api_key}"
    req = requests.get(url)
    results = req.json().get('results', [])
    if not results:
        return f"Location ({latlang})"
    return results[0]['formatted_address']


# add = reverse_geocoding('23.7465882,90.3846205')
# print(add)
