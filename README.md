# 🚌 Namma Transit
![Python](https://img.shields.io/badge/Python-3.14-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

A smart, user-friendly web app to navigate **Bengaluru's public transport** — BMTC buses and Namma Metro — built with Python and Django.

---

## Features

- **Find Directions** — Enter a source and destination to get all direct buses and metro lines, with distance, ETA, and route timeline
- **Multi-modal Interchange** — Suggests bus + metro combinations via interchange stops
- **Find Specific Bus** — Search by bus number (e.g. `401K`, `335E`, `500C`) to see the full route
- **Nearby Stations** — Uses your live location to show nearby bus stops on a Google Map
- **All Bus Routes** — Browse all 25 BMTC and Namma Metro routes in a searchable table
- **Crowd Reporting** — Report how crowded a bus is in real time (Empty / Moderate / Full / Overcrowded)
- **Auto Fare Estimator** — Calculate last-mile auto-rickshaw cost based on distance and time of day
- **Rain Alert** — Warns about heavy rain and flood-prone stops in Bengaluru
- **Google Maps Button** — Opens the full route directly in Google Maps
- **Autocomplete** — Smart suggestions for Bengaluru stops and bus numbers

---

## Tech Stack

- **Backend:** Python 3.14, Django 5.2
- **Frontend:** Bootstrap 4, HTML/CSS/JS
- **Database:** SQLite (dev)
- **APIs:** Google Maps (Geocoding, Distance Matrix, Nearby Places), OpenWeatherMap
- **Other:** Haversine fallback for distance when Maps API unavailable

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/PPViveka/namma-transit.git
cd namma-transit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file with your API keys
#    KEY2=your_google_maps_api_key
#    OPENWEATHER_KEY=your_openweathermap_key  (optional)

# 4. Apply migrations
python manage.py migrate

# 5. Load bus data
python manage.py loaddata home_page/fixtures/bengaluru_buses.json

# 6. Run the server
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in your browser.

---

## Bus Routes Included

25 verified BMTC and Namma Metro routes including:

| Bus | Route |
|-----|-------|
| 335E | Majestic → Kadugodi |
| 401 | Yelahanka → Yeshwanthpur |
| 401B | Hampinagara → Yelahanka |
| 401K | Yelahanka → Kengeri |
| 500A | Hebbala → Banashankari |
| 500C | KR Puram → Silk Board (Vajra) |
| 500D | Silk Board → Hebbala (Vajra) |
| 298M | Majestic → Airport (Vajra) |
| Metro Purple Line | Kengeri ↔ Baiyappanahalli / Whitefield |
| Metro Green Line | Nagasandra ↔ Silk Board |
| ...and more | |

---

## Author

**Viveka** — [@PPViveka](https://github.com/PPViveka)

---

## License

MIT License — Copyright (c) 2025 Viveka
