from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_MILES = 3958.7613


@dataclass(frozen=True)
class RouteCandidate:
    station_id: int
    station_name: str
    city: str
    state: str
    latitude: float
    longitude: float
    price_per_gallon: float
    route_mile: float
    off_route_miles: float


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_r = radians(lat1)
    lon1_r = radians(lon1)
    lat2_r = radians(lat2)
    lon2_r = radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(a))


def cumulative_route_miles(coordinates: list[list[float]]) -> list[float]:
    miles = [0.0]
    for idx in range(1, len(coordinates)):
        prev_lng, prev_lat = coordinates[idx - 1]
        lng, lat = coordinates[idx]
        miles.append(miles[-1] + haversine_miles(prev_lat, prev_lng, lat, lng))
    return miles


def route_length_miles(coordinates: list[list[float]]) -> float:
    if len(coordinates) < 2:
        return 0.0
    return cumulative_route_miles(coordinates)[-1]


def nearest_route_point(
    coordinates: list[list[float]], station_lat: float, station_lng: float
) -> tuple[int, float]:
    closest_index = 0
    closest_distance = float("inf")

    for index, (lng, lat) in enumerate(coordinates):
        distance = haversine_miles(station_lat, station_lng, lat, lng)
        if distance < closest_distance:
            closest_distance = distance
            closest_index = index

    return closest_index, closest_distance
