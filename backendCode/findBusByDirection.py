import hashlib
import time as _time
import math

import googlemaps
from decouple import config
from django.core.cache import cache

api_key = config('KEY2')

_CACHE_TTL = 900  # 15 minutes — traffic changes; don't cache longer

# Approximate coordinates for known Bengaluru stops (lat, lng)
_STOP_COORDS = {
    # ---- Core city ----
    'majestic': (12.9767, 77.5713),
    'kr circle': (12.9767, 77.5960),
    'kr market': (12.9617, 77.5764),
    'mg road': (12.9758, 77.6060),
    'cubbon park': (12.9763, 77.5929),
    'vidhana soudha': (12.9793, 77.5908),
    'shivajinagar': (12.9851, 77.6006),
    'richmond circle': (12.9627, 77.6019),
    'richmond town': (12.9633, 77.6010),
    'ulsoor': (12.9823, 77.6196),
    'halasuru': (12.9812, 77.6224),
    'indiranagar': (12.9784, 77.6408),
    'domlur': (12.9608, 77.6391),
    'hal': (12.9600, 77.6659),
    'old airport road': (12.9721, 77.6516),
    'city railway station': (12.9776, 77.5714),
    'sadashivanagar': (13.0085, 77.5741),
    'mekhri circle': (13.0069, 77.5692),
    'ananda rao circle': (12.9802, 77.5700),
    # ---- South ----
    'silk board': (12.9176, 77.6233),
    'koramangala': (12.9352, 77.6245),
    'btm layout': (12.9165, 77.6101),
    'hsr layout': (12.9081, 77.6476),
    'jayanagar': (12.9299, 77.5827),
    'jp nagar': (12.9078, 77.5847),
    'banashankari': (12.9255, 77.5468),
    'national college': (12.9487, 77.5769),
    'lalbagh': (12.9507, 77.5848),
    'lakkasandra': (12.9334, 77.5924),
    'shanthinagara': (12.9495, 77.5875),
    'nimhans': (12.9399, 77.5953),
    'dairy circle': (12.9283, 77.5912),
    'basavanagudi': (12.9432, 77.5748),
    'minerva circle': (12.9468, 77.5836),
    'rv road': (12.9422, 77.5833),
    'jayadeva': (12.9278, 77.6019),
    'bommanahalli': (12.8951, 77.6402),
    'electronic city': (12.8399, 77.6770),
    'hulimavu': (12.8781, 77.6090),
    'bannerughatta': (12.8584, 77.5987),
    'bannerghatta road': (12.8872, 77.5978),
    'begur': (12.8613, 77.6249),
    'bommasandra': (12.7962, 77.6852),
    'uttarahalli': (12.9000, 77.5450),
    # ---- West ----
    'vijayanagar': (12.9725, 77.5330),
    'vijayanagara': (12.9725, 77.5330),
    'magadi road': (12.9725, 77.5457),
    'mysuru road': (12.9461, 77.5122),
    'mysore road': (12.9461, 77.5122),
    'nayandahalli': (12.9510, 77.5243),
    'deepanjalinagar': (12.9685, 77.5118),
    'hampinagara': (12.9760, 77.5245),
    'sirsi circle': (12.9556, 77.5646),
    'rv college': (12.9149, 77.4990),
    'kengeri': (12.9122, 77.4826),
    'kambipura': (12.9044, 77.4760),
    'hampapura': (12.9088, 77.4866),
    'nagarabhavi': (12.9593, 77.5027),
    'rpc layout': (12.9628, 77.5270),
    'kanakapura road': (12.8905, 77.5786),
    # ---- North ----
    'rajajinagar': (12.9922, 77.5541),
    'mathikere': (13.0143, 77.5533),
    'bel circle': (13.0291, 77.5599),
    'yeshwanthpur': (13.0201, 77.5397),
    'malleshwaram': (13.0031, 77.5724),
    'goraguntepalya': (13.0206, 77.5268),
    'peenya': (13.0288, 77.5179),
    'peenya industry': (13.0308, 77.5124),
    'nagasandra': (13.0437, 77.5124),
    'jalahalli': (13.0357, 77.5168),
    'chikkabanavara': (13.0710, 77.4914),
    'hesaraghatta': (13.1013, 77.4633),
    'tumkur road': (13.0116, 77.5376),
    'vidyaranyapura': (13.0671, 77.5529),
    'hebbal': (13.0354, 77.5970),
    'sadashivanagar': (13.0085, 77.5741),
    'kogilu': (13.0755, 77.5918),
    'kogilu cross': (13.0720, 77.5930),
    'jakkur': (13.0695, 77.5934),
    'yelahanka': (13.1007, 77.5963),
    'yelahanka new town': (13.1052, 77.5940),
    'bellary road': (13.0707, 77.5936),
    'kempapura': (13.0402, 77.5876),
    'bagalur': (13.1583, 77.6533),
    'devanahalli': (13.2469, 77.7148),
    'kempegowda international airport': (13.1986, 77.7066),
    # ---- North-east ----
    'nagavara': (13.0448, 77.6328),
    'manyatha tech park': (13.0483, 77.6350),
    'nagawara': (13.0454, 77.6218),
    'hennur': (13.0380, 77.6388),
    'banasawadi': (13.0092, 77.6379),
    'coles park': (12.9920, 77.6044),
    'kr puram': (13.0071, 77.6958),
    'tin factory': (13.0027, 77.6588),
    'ramamurthynagar': (13.0048, 77.6671),
    'baiyappanahalli': (12.9988, 77.6483),
    # ---- East ----
    'marathahalli': (12.9591, 77.6971),
    'bellandur': (12.9299, 77.6749),
    'sarjapura': (12.8640, 77.7864),
    'sarjapur road': (12.9120, 77.6748),
    'gunjur palya': (12.9073, 77.7127),
    'itpl': (12.9860, 77.7279),
    'whitefield': (12.9698, 77.7499),
    'kadugodi': (12.9951, 77.7483),
    'chandapura': (12.7993, 77.6820),
    'anekal': (12.7101, 77.6960),
    'nelamangala': (13.0975, 77.3927),
    'jayanagar 4th block': (12.9283, 77.5837),
}


def _haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _estimate_distance(route_labels):
    """Rough road-distance estimate when the Maps API is unavailable.
    Uses known coordinates; falls back to 2 km/hop for unknown stops.
    Applies a 1.35× road-factor to straight-line distances.
    Speed assumed 20 km/h (Bengaluru mixed traffic).
    """
    total_km = 0.0
    for i in range(len(route_labels) - 1):
        a = route_labels[i].lower().replace(' bus stop, bengaluru', '').strip()
        b = route_labels[i + 1].lower().replace(' bus stop, bengaluru', '').strip()
        ca = _STOP_COORDS.get(a)
        cb = _STOP_COORDS.get(b)
        if ca and cb:
            total_km += _haversine_km(*ca, *cb) * 1.35
        else:
            total_km += 2.0  # 2 km default per hop
    speed_kmh = 20
    duration_min = int((total_km / speed_kmh) * 60)
    return round(total_km, 2), duration_min


def find_distance(route):
    """
    Return (total_distance_km, total_duration_min) for the given stop sequence.
    Tries Google Maps Distance Matrix; falls back to Haversine estimate on error.
    Results are cached for 15 minutes per unique route.
    """
    cache_key = 'gmaps_' + hashlib.md5(','.join(route).encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    for i in range(len(route)):
        route[i] = route[i] + ' Bus Stop, Bengaluru'

    try:
        total_distance = 0.0
        total_duration_min = 0
        gmaps = googlemaps.Client(api_key)
        departure = int(_time.time())

        for i in range(len(route) - 1):
            ori = route[i]
            des = route[i + 1]
            result = gmaps.distance_matrix(
                ori, des,
                region='IN',
                departure_time=departure,
                traffic_model='best_guess',
            )
            elem = result['rows'][0]['elements'][0]
            if elem.get('status') != 'OK':
                raise ValueError(f"Maps API element status: {elem.get('status')}")

            dist_text = elem['distance']['text']
            if dist_text.endswith(' m'):
                km = float(dist_text[:-2]) / 1000
            else:
                km = float(dist_text[:-3])
            total_distance += km

            dur_block = elem.get('duration_in_traffic') or elem.get('duration', {})
            total_duration_min += dur_block.get('value', 0) // 60

        result_tuple = (round(total_distance, 2), total_duration_min)
    except Exception:
        result_tuple = _estimate_distance(route)

    cache.set(cache_key, result_tuple, _CACHE_TTL)
    return result_tuple
