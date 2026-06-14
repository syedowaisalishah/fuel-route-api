from dataclasses import dataclass
from hashlib import sha256
from json import loads
from urllib.request import urlopen

from django.conf import settings
from django.core.cache import cache


class RouteLookupError(Exception):
    pass


@dataclass(frozen=True)
class RouteResult:
    distance_meters: float
    duration_seconds: float
    geometry: dict


class RoutingService:
    def get_route(self, start_lat: float, start_lng: float, finish_lat: float, finish_lng: float) -> RouteResult:
        cache_key = self._cache_key(start_lat, start_lng, finish_lat, finish_lng)
        cached = cache.get(cache_key)
        if cached:
            return RouteResult(**cached)

        coordinates = f"{start_lng},{start_lat};{finish_lng},{finish_lat}"
        url = (
            f"{settings.OSRM_BASE_URL}/route/v1/driving/{coordinates}"
            "?overview=full&geometries=geojson&steps=false&alternatives=false"
        )

        try:
            with urlopen(url, timeout=settings.EXTERNAL_API_TIMEOUT_SECONDS) as response:
                payload = loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network failure path
            raise RouteLookupError("Unable to fetch route from routing service") from exc

        if payload.get("code") != "Ok" or not payload.get("routes"):
            raise RouteLookupError("No route found between the provided locations")

        route = payload["routes"][0]
        result = RouteResult(
            distance_meters=float(route["distance"]),
            duration_seconds=float(route["duration"]),
            geometry=route["geometry"],
        )
        cache.set(cache_key, result.__dict__, settings.ROUTE_CACHE_TIMEOUT_SECONDS)
        return result

    def _cache_key(self, start_lat: float, start_lng: float, finish_lat: float, finish_lng: float) -> str:
        raw_key = f"{start_lat:.6f},{start_lng:.6f}:{finish_lat:.6f},{finish_lng:.6f}"
        digest = sha256(raw_key.encode("utf-8")).hexdigest()
        return f"route_driving_{digest}"
