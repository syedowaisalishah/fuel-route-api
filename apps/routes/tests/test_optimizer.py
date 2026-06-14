from django.test import TestCase

from apps.routes.models import FuelStation
from apps.routes.services.optimizer import FuelRouteOptimizer


class FuelRouteOptimizerTests(TestCase):
    def test_builds_candidate_stops_inside_route_corridor(self):
        FuelStation.objects.create(
            name="Near Start",
            address="1 Main",
            city="Austin",
            state="TX",
            latitude=30.2672,
            longitude=-97.7431,
            price_per_gallon="3.49",
        )
        FuelStation.objects.create(
            name="Mid Route",
            address="2 Main",
            city="Waco",
            state="TX",
            latitude=31.5493,
            longitude=-97.1467,
            price_per_gallon="3.29",
        )
        FuelStation.objects.create(
            name="Far Away",
            address="3 Main",
            city="Miami",
            state="FL",
            latitude=25.7617,
            longitude=-80.1918,
            price_per_gallon="2.99",
        )

        route_geometry = {
            "type": "LineString",
            "coordinates": [
                [-97.7431, 30.2672],
                [-97.1467, 31.5493],
                [-96.7970, 32.7767],
            ],
        }

        stops, total_cost = FuelRouteOptimizer().build_stop_plan(route_geometry)

        self.assertGreaterEqual(len(stops), 1)
        self.assertGreater(total_cost, 0)
        self.assertTrue(all(stop.city in {"Austin", "Waco"} for stop in stops))

    def test_buys_at_start_station_when_destination_is_reachable(self):
        FuelStation.objects.create(
            name="Expensive Near",
            address="1 Main",
            city="Austin",
            state="TX",
            latitude=30.2672,
            longitude=-97.7431,
            price_per_gallon="3.79",
        )
        FuelStation.objects.create(
            name="Cheaper Mid",
            address="2 Main",
            city="Temple",
            state="TX",
            latitude=31.0982,
            longitude=-97.3428,
            price_per_gallon="3.19",
        )

        route_geometry = {
            "type": "LineString",
            "coordinates": [
                [-97.7431, 30.2672],
                [-97.3428, 31.0982],
                [-96.7970, 32.7767],
            ],
        }

        stops, _ = FuelRouteOptimizer().build_stop_plan(route_geometry)

        self.assertEqual(stops[0].name, "Expensive Near")
        self.assertGreater(stops[0].gallons_purchased, 0)
