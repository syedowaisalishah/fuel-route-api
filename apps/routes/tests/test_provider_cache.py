from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.routes.services.geocoding_service import GeocodingService
from apps.routes.services.routing_service import RoutingService


class ProviderCacheTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(EXTERNAL_API_TIMEOUT_SECONDS=1)
    @patch("apps.routes.services.geocoding_service.urlopen")
    def test_geocoding_results_are_cached(self, mock_urlopen):
        response = Mock()
        response.read.return_value = (
            b'[{"display_name":"Austin, Texas, United States","lat":"30.2672","lon":"-97.7431"}]'
        )
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = response

        service = GeocodingService()
        first = service.resolve_us_location("Austin, TX")
        second = service.resolve_us_location("Austin, TX")

        self.assertEqual(first.latitude, second.latitude)
        self.assertEqual(mock_urlopen.call_count, 1)

    @override_settings(EXTERNAL_API_TIMEOUT_SECONDS=1)
    @patch("apps.routes.services.routing_service.urlopen")
    def test_route_results_are_cached(self, mock_urlopen):
        response = Mock()
        response.read.return_value = (
            b'{"code":"Ok","routes":[{"distance":321869.0,"duration":14400.0,'
            b'"geometry":{"type":"LineString","coordinates":[[-97.7431,30.2672],[-96.797,32.7767]]}}]}'
        )
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = response

        service = RoutingService()
        first = service.get_route(30.2672, -97.7431, 32.7767, -96.7970)
        second = service.get_route(30.2672, -97.7431, 32.7767, -96.7970)

        self.assertEqual(first.distance_meters, second.distance_meters)
        self.assertEqual(mock_urlopen.call_count, 1)
