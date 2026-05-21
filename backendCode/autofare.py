from datetime import datetime

BASE_FARE = 30.0       # ₹ flag-down charge
PER_KM_DAY = 15.0     # ₹/km (05:00–22:00)
PER_KM_NIGHT = 22.5   # ₹/km (22:00–05:00, 1.5× day rate)
MINIMUM_FARE = 30.0   # ₹ floor


def estimate_auto_fare(distance_km: float, hour: int = None) -> dict:
    """
    Estimate auto-rickshaw fare for distance_km using the KSRTC Bengaluru
    tariff (₹30 base, ₹15/km day, ₹22.50/km night, minimum ₹30).
    """
    if hour is None:
        hour = datetime.now().hour
    is_night = hour >= 22 or hour < 5
    per_km = PER_KM_NIGHT if is_night else PER_KM_DAY
    fare = max(BASE_FARE + distance_km * per_km, MINIMUM_FARE)
    return {
        'distance_km': round(distance_km, 2),
        'fare': round(fare),
        'is_night': is_night,
        'breakdown': f'₹{int(BASE_FARE)} base + ₹{per_km}/km × {round(distance_km, 2)} km',
        'tariff_note': 'Night tariff (1.5×) applies 10 pm – 5 am' if is_night else 'Day tariff',
    }
