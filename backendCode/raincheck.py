import requests
from decouple import config, UndefinedValueError

# Stops historically prone to waterlogging in Bengaluru
FLOOD_PRONE_STOPS = {
    'KR Puram', 'Silk Board', 'Marathahalli', 'Hebbal',
    'Koramangala', 'Bellandur', 'Tin Factory', 'Whitefield',
    'Bannerghatta Road', 'HSR Layout', 'BTM Layout',
}

# OpenWeatherMap rain intensity threshold for "heavy rain" in mm/hr
HEAVY_RAIN_THRESHOLD_MM = 7.5


def get_rain_alert():
    """
    Return (is_heavy_rain: bool, affected_stops: list) for current Bengaluru weather.
    Requires OPENWEATHER_KEY in .env.  Returns (False, []) if key is absent or
    the API call fails — never raises.
    """
    try:
        api_key = config('OPENWEATHER_KEY')
    except UndefinedValueError:
        return False, []

    try:
        r = requests.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params={'q': 'Bengaluru,IN', 'appid': api_key, 'units': 'metric'},
            timeout=3,
        )
        data = r.json()
        weather_id = data.get('weather', [{}])[0].get('id', 0)
        rain_1h = data.get('rain', {}).get('1h', 0)
        # OpenWeatherMap: 5xx codes = rain family; heavy = ≥502 or rainfall ≥ threshold
        is_heavy = (500 <= weather_id <= 531) and (rain_1h >= HEAVY_RAIN_THRESHOLD_MM)
        return is_heavy, list(FLOOD_PRONE_STOPS) if is_heavy else []
    except Exception:
        return False, []
