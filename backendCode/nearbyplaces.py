import math
import requests
from urllib.parse import urlencode
from decouple import config

api_key = config('KEY2')

_NEARBY_RADIUS_M = 500   # Google Places search radius
_DB_RADIUS_KM = 0.75     # Haversine fallback radius for interchange stops


def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two lat/lng points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _nearby_from_db(lat, lng, radius_km=_DB_RADIUS_KM):
    """
    Haversine-based fallback: return interchange stops within radius_km.
    Works with SQLite and requires no external API call.
    When PostGIS is enabled this can be replaced with ST_DWithin for O(log n).
    """
    from home_page.models import Interchange
    results = []
    for ix in Interchange.objects.exclude(lat=None).exclude(lng=None):
        if _haversine_km(float(lat), float(lng), ix.lat, ix.lng) <= radius_km:
            results.append(f"{ix.stop_name}, Bengaluru, India")
    return sorted(results)


def search_nearby_places(lat, lng):
    """
    Return a de-duplicated list of nearby bus stop address strings.
    Primary source: Google Places API (radius 500 m, keyword 'Bus stop').
    Fallback: Interchange table via Haversine distance when Places returns nothing.
    """
    places_endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": f"{lat},{lng}",
        "radius": _NEARBY_RADIUS_M,
        "keyword": "Bus stop",
    }
    try:
        r = requests.get(f"{places_endpoint}?{urlencode(params)}", timeout=5)
        nearby_places_list = [
            item['name'] + ', ' + item['vicinity'] + ', India'
            for item in r.json().get('results', [])
        ]
        result = list(dict.fromkeys(nearby_places_list))
    except Exception:
        result = []

    if not result:
        result = _nearby_from_db(lat, lng)

    return result
