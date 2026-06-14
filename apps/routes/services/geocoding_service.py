from dataclasses import dataclass
from hashlib import sha256
from json import loads
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


class LocationLookupError(Exception):
    pass


@dataclass(frozen=True)
class GeocodedLocation:
    query: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str | None = None


class GeocodingService:
    def resolve_us_location(self, query: str) -> GeocodedLocation:
        cache_key = self._cache_key(query)
        cached = cache.get(cache_key)
        if cached:
            return GeocodedLocation(**cached)

        params = urlencode(
            {
                "q": query,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "us",
            }
        )
        request = Request(
            f"{settings.NOMINATIM_BASE_URL}?{params}",
            headers={"User-Agent": settings.NOMINATIM_USER_AGENT, "Accept": "application/json"},
        )

        try:
            with urlopen(request, timeout=settings.EXTERNAL_API_TIMEOUT_SECONDS) as response:
                payload = loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network failure path
            raise LocationLookupError(f"Unable to geocode location: {query}") from exc

        if not payload:
            raise LocationLookupError(f"Location not found in the USA: {query}")

        item = payload[0]
        location = GeocodedLocation(
            query=query,
            display_name=item.get("display_name", query),
            latitude=float(item["lat"]),
            longitude=float(item["lon"]),
            country_code=item.get("address", {}).get("country_code"),
        )
        cache.set(cache_key, location.__dict__, settings.GEOCODING_CACHE_TIMEOUT_SECONDS)
        return location

    def _cache_key(self, query: str) -> str:
        digest = sha256(query.strip().lower().encode("utf-8")).hexdigest()
        return f"geocode_us_{digest}"
