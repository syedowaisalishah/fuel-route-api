from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class FuelPlanApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("apps.routes.services.fuel_plan_service.GeocodingService.resolve_us_location")
    @patch("apps.routes.services.fuel_plan_service.RoutingService.get_route")
    def test_fuel_plan_uses_live_route_payload_shape(self, mock_route, mock_geocode):
        mock_geocode.side_effect = [
            type("Geo", (), {"display_name": "Austin, TX, USA", "latitude": 30.2672, "longitude": -97.7431})(),
            type("Geo", (), {"display_name": "Dallas, TX, USA", "latitude": 32.7767, "longitude": -96.7970})(),
        ]
        mock_route.return_value = type(
            "Route",
            (),
            {
                "distance_meters": 321869.0,
                "duration_seconds": 14400.0,
                "geometry": {"type": "LineString", "coordinates": [[-97.7431, 30.2672], [-96.7970, 32.7767]]},
            },
        )()

        response = self.client.post(
            "/api/routes/fuel-plan/",
            data={"start": "Austin, TX", "finish": "Dallas, TX"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["start"], "Austin, TX")
        self.assertEqual(response.data["finish"], "Dallas, TX")
        self.assertEqual(response.data["distance_miles"], Decimal("200.0"))
        self.assertEqual(response.data["fuel_required_gallons"], Decimal("20.00"))
        self.assertEqual(response.data["route_geometry"]["type"], "LineString")
        self.assertIn("assumptions", response.data)

    def test_rejects_same_start_and_finish(self):
        response = self.client.post(
            "/api/routes/fuel-plan/",
            data={"start": "Austin, TX", "finish": "Austin, TX"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
