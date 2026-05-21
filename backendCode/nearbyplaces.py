import math
import requests
from urllib.parse import urlencode
from decouple import config

api_key = config('KEY2')

_NEARBY_RADIUS_M = 500   # Google Places search radius in metres
_DB_RADIUS_KM    = 0.75  # Haversine fallback — initial search radius
_DB_MAX_KM       = 5.0   # Haversine fallback — expanded search radius


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi   = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _nearby_from_db(lat, lng):
    """
    Haversine fallback: return interchange stops as dicts {name, lat, lng}.
    Expands radius progressively; always returns at least the 3 nearest stops.
    """
    from home_page.models import Interchange
    distances = []
    for ix in Interchange.objects.exclude(lat=None).exclude(lng=None):
        dist = _haversine_km(float(lat), float(lng), float(ix.lat), float(ix.lng))
        distances.append((dist, ix.stop_name, float(ix.lat), float(ix.lng)))
    distances.sort(key=lambda x: x[0])

    results, seen = [], set()

    for dist, name, ilat, ilng in distances:
        if dist <= _DB_RADIUS_KM and name not in seen:
            results.append({'name': f"{name}, Bengaluru, India", 'lat': ilat, 'lng': ilng})
            seen.add(name)

    if len(results) < 3:
        for dist, name, ilat, ilng in distances:
            if _DB_RADIUS_KM < dist <= _DB_MAX_KM and name not in seen:
                results.append({'name': f"{name}, Bengaluru, India", 'lat': ilat, 'lng': ilng})
                seen.add(name)

    if not results and distances:
        for dist, name, ilat, ilng in distances[:3]:
            if name not in seen:
                results.append({'name': f"{name}, Bengaluru, India", 'lat': ilat, 'lng': ilng})
                seen.add(name)

    return results


def search_nearby_places(lat, lng):
    """
    Return a list of dicts {name, lat, lng} for nearby bus stops.
    Primary: Google Places API (500 m radius, keyword 'Bus stop').
    Fallback: Interchange table via Haversine when Places returns nothing.
    """
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": f"{lat},{lng}",
        "radius": _NEARBY_RADIUS_M,
        "keyword": "Bus stop",
    }
    try:
        r = requests.get(
            f"{endpoint}?{urlencode(params)}",
            headers={'Referer': 'http://localhost:8000'},
            timeout=5,
        )
        raw = r.json().get('results', [])
        seen, result = set(), []
        for item in raw:
            name = item['name'] + ', ' + item['vicinity'] + ', India'
            if name not in seen:
                seen.add(name)
                result.append({
                    'name': name,
                    'lat': item['geometry']['location']['lat'],
                    'lng': item['geometry']['location']['lng'],
                })
    except Exception:
        result = []

    if not result:
        result = _nearby_from_db(lat, lng)

    return result
