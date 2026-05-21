import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from home_page.models import Route, BusInformation, Interchange, CrowdReport
from backendCode.autofare import estimate_auto_fare
from backendCode.raincheck import get_rain_alert
from backendCode.findBusByDirection import _haversine_km, _estimate_distance

class SmartTrackingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Create Route structures
        self.route_bus = Route.objects.create(
            routes="Majestic, Hebbal, Yelahanka"
        )
        self.route_metro = Route.objects.create(
            routes="Yelahanka, Yeshwanthpur, Nagasandra"
        )
        
        # 2. Create Bus/Metro Information
        self.bus = BusInformation.objects.create(
            bus_name="401K",
            bus_sourcetodestination="Majestic-Yelahanka",
            bus_viaroad="Majestic, Hebbal, Yelahanka",
            bus_type="ORDINARY",
            mode="BUS",
            route_id=self.route_bus
        )
        self.metro = BusInformation.objects.create(
            bus_name="Metro Green Line",
            bus_sourcetodestination="Yelahanka-Nagasandra",
            bus_viaroad="Yelahanka, Yeshwanthpur, Nagasandra",
            bus_type="AC",
            mode="METRO",
            route_id=self.route_metro
        )
        
        # 3. Create Interchange stops
        self.interchange = Interchange.objects.create(
            stop_name="Yelahanka",
            modes_available="BUS,METRO",
            lat=13.1007,
            lng=77.5963
        )

    def test_get_views_redirects(self):
        """Verify that GET requests to search, directions, and bus detail views redirect gracefully to home."""
        endpoints = ['finddirection', 'searchnearby_address', 'searchnearby_latlng', 'findspecificbus']
        for ep in endpoints:
            response = self.client.get(reverse(ep))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('home'))

    def test_auto_fare_calculation_daytime(self):
        """Test daytime auto fare calculation (₹30 base, ₹15/km, minimum ₹30)."""
        # Distance 0.5 km (base ₹30 + ₹7.5 = ₹37.5 -> ₹38)
        res = estimate_auto_fare(0.5, hour=12)
        self.assertEqual(res['fare'], 38)
        self.assertFalse(res['is_night'])
        
        # Distance 10 km (base ₹30 + ₹150 = ₹180)
        res = estimate_auto_fare(10.0, hour=12)
        self.assertEqual(res['fare'], 180)

    def test_auto_fare_calculation_nighttime(self):
        """Test nighttime auto fare calculation (₹30 base, ₹22.50/km, minimum ₹30)."""
        # Distance 5 km (base ₹30 + ₹112.5 = ₹142.5 -> ₹142 due to banker's rounding)
        res = estimate_auto_fare(5.0, hour=23)
        self.assertTrue(res['is_night'])
        self.assertEqual(res['fare'], 142)

    def test_auto_fare_ajax_endpoint(self):
        """Test the AJAX endpoint /smartTracking/auto_fare/ returns JSON correctly."""
        response = self.client.post(reverse('auto_fare'), {'distance_km': '5.0'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['ok'])
        self.assertEqual(data['distance_km'], 5.0)

    @patch('requests.get')
    def test_rain_alert_heavy(self, mock_get):
        """Test heavy rain alerts and waterlog checks when OpenWeatherMap returns code 500 and rain volume."""
        mock_response = {
            'weather': [{'id': 501}],
            'rain': {'1h': 8.0}
        }
        mock_get.return_value.json.return_value = mock_response
        
        # Weather key is configured
        with patch('backendCode.raincheck.config', return_value='test_key'):
            is_heavy, affected = get_rain_alert()
            self.assertTrue(is_heavy)
            self.assertIn('Silk Board', affected)

    @patch('requests.get')
    def test_rain_alert_light(self, mock_get):
        """Test light rain triggers no warnings."""
        mock_response = {
            'weather': [{'id': 500}],
            'rain': {'1h': 2.0}
        }
        mock_get.return_value.json.return_value = mock_response
        with patch('backendCode.raincheck.config', return_value='test_key'):
            is_heavy, affected = get_rain_alert()
            self.assertFalse(is_heavy)

    def test_haversine_distance_calculation(self):
        """Verify the Great-circle haversine distance calculation is accurate."""
        # Majestic to Yelahanka approx 14 km straight line
        dist = _haversine_km(12.9767, 77.5713, 13.1007, 77.5963)
        self.assertTrue(10.0 < dist < 20.0)

    def test_estimate_distance_fallback(self):
        """Test the Haversine segment router fallback for pre-mapped stops."""
        km, mins = _estimate_distance(['Majestic', 'Hebbal', 'Yelahanka'])
        self.assertTrue(km > 0)
        self.assertTrue(mins > 0)

    def test_find_directions_direct(self):
        """Test finding a direct route from Majestic to Yelahanka returns the correct bus."""
        response = self.client.post(reverse('finddirection'), {
            'from': 'Majestic',
            'to': 'Yelahanka'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "401K")
        self.assertContains(response, "Distance:")

    def test_find_directions_interchange(self):
        """Test finding a multi-modal route from Majestic to Yeshwanthpur via Yelahanka."""
        response = self.client.post(reverse('finddirection'), {
            'from': 'Majestic',
            'to': 'Yeshwanthpur'
        })
        self.assertEqual(response.status_code, 200)
        # Should suggest leg A (401K) + Interchange (Yelahanka) + leg B (Green Line)
        self.assertContains(response, "Multi-modal <span>Interchange Options</span>")
        self.assertContains(response, "401K")
        self.assertContains(response, "Metro Green Line")
        self.assertContains(response, "Change at <strong>Yelahanka</strong>")

    def test_find_specific_bus_exact(self):
        """Test searching specifically for '401K'."""
        response = self.client.post(reverse('findspecificbus'), {
            'bus_name': '401K'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "401K")
        self.assertContains(response, "Majestic")
        self.assertContains(response, "Yelahanka")

    def test_find_specific_bus_prefix_fallback(self):
        """Test searching specifically for '401B' falls back to matching '401K'."""
        response = self.client.post(reverse('findspecificbus'), {
            'bus_name': '401B'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "401K")

    def test_all_buses_list(self):
        """Verify the 'All Buses' list view returns loaded routes."""
        response = self.client.get(reverse('allbuses'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "401K")
        self.assertContains(response, "Metro Green Line")

    def test_crowd_reporting_flow(self):
        """Submit a crowd report via AJAX and assert it appears in subsequent direction searches."""
        # 1. Post a crowd report for 401K
        response = self.client.post(reverse('crowd_report'), {
            'bus_id': self.bus.bus_id,
            'status': 'FULL'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['ok'])
        
        # Verify saved in DB
        report = CrowdReport.objects.latest()
        self.assertEqual(report.status, 'FULL')
        self.assertEqual(report.bus, self.bus)
        
        # 2. Query directions which returns 401K
        response = self.client.post(reverse('finddirection'), {
            'from': 'Majestic',
            'to': 'Yelahanka'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Full")
