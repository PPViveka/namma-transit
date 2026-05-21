import requests
from urllib.parse import urlencode
from decouple import config

api_key = config('KEY2')


def geocoding_from_address(address):
    # Try to find a matching interchange in our database first for perfect offline lookup!
    query = address.strip().lower()
    try:
        from home_page.models import Interchange
        for ix in Interchange.objects.exclude(lat=None).exclude(lng=None):
            if ix.stop_name.lower() in query or query in ix.stop_name.lower():
                return {
                    'formatted_address': f"{ix.stop_name}, Bengaluru, India",
                    'lat': ix.lat,
                    'lng': ix.lng,
                }
    except Exception:
        pass

    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address + ", Bengaluru, Karnataka, India", 'region': 'in', "key": api_key}
    url_params = urlencode(params)

    url = f"{endpoint}?{url_params}"
    resp = requests.get(url, headers={'Referer': 'http://localhost:8000'})
    body = resp.json()
    if body.get('status') != 'OK':
        import logging
        logging.warning("Geocoding API error: %s — %s", body.get('status'), body.get('error_message', ''))
    results = body.get('results', [])
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



def reverse_geocoding(latlang):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json"
    url = f"{endpoint}?latlng={latlang}&region=in&key={api_key}"
    req = requests.get(url)
    results = req.json().get('results', [])
    if not results:
        return f"Location ({latlang})"
    return results[0]['formatted_address']
