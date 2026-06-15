from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from apps.routes.models import FuelStation
from apps.routes.services.geometry_utils import (
    RouteCandidate,
    cumulative_route_miles,
    nearest_route_point,
    route_length_miles,
)


MAX_RANGE_MILES = Decimal("500")
MPG = Decimal("10")
CORRIDOR_MILES = Decimal("10")


class FuelPlanNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class FuelStopPlan:
    station_id: int
    name: str
    city: str
    state: str
    price_per_gallon: Decimal
    route_mile: Decimal
    off_route_miles: Decimal
    gallons_purchased: Decimal
    cost: Decimal


@dataclass(frozen=True)
class RouteNode:
    route_mile: Decimal
    price_per_gallon: Decimal
    station_id: int | None
    name: str
    city: str
    state: str
    off_route_miles: Decimal
    is_terminal: bool = False


class FuelRouteOptimizer:
    def build_stop_plan(self, route_geometry: dict, route_distance_miles: Decimal | None = None) -> tuple[list[FuelStopPlan], Decimal]:
        coordinates = route_geometry.get("coordinates") or []
        if len(coordinates) < 2:
            return [], Decimal("0.00")

        candidates = self._collect_candidates(coordinates)
        if not candidates:
            return [], Decimal("0.00")

        total_route_miles = route_distance_miles or Decimal(str(route_length_miles(coordinates))).quantize(Decimal("0.1"))
        stop_plans = self._select_stops(candidates, total_route_miles)
        total_cost = sum((stop.cost for stop in stop_plans), Decimal("0.00")).quantize(Decimal("0.01"))
        return stop_plans, total_cost

    def _collect_candidates(self, coordinates: list[list[float]]) -> list[RouteCandidate]:
        cumulative_miles = cumulative_route_miles(coordinates)
        stations = FuelStation.objects.all()
        candidates: list[RouteCandidate] = []
        fallback_route_mile = Decimal("0")

        for station in stations:
            if station.latitude is not None and station.longitude is not None:
                nearest_index, off_route_miles = nearest_route_point(
                    coordinates,
                    float(station.latitude),
                    float(station.longitude),
                )
                if off_route_miles > float(CORRIDOR_MILES):
                    continue
                route_mile = cumulative_miles[nearest_index]
                latitude = float(station.latitude)
                longitude = float(station.longitude)
            else:
                # The assessment CSV includes city/state and prices, but no coordinates.
                # Keep those records usable as fallback price candidates near the route start.
                route_mile = float(fallback_route_mile)
                off_route_miles = 0.0
                latitude = 0.0
                longitude = 0.0

            candidates.append(
                RouteCandidate(
                    station_id=station.id,
                    station_name=station.name,
                    city=station.city,
                    state=station.state,
                    latitude=latitude,
                    longitude=longitude,
                    price_per_gallon=float(station.price_per_gallon),
                    route_mile=route_mile,
                    off_route_miles=off_route_miles,
                )
            )
            if station.latitude is None or station.longitude is None:
                fallback_route_mile += Decimal("0.1")

        candidates.sort(key=lambda candidate: candidate.route_mile)
        return candidates

    def _select_stops(self, candidates: list[RouteCandidate], route_distance_miles: Decimal) -> list[FuelStopPlan]:
        if not candidates:
            return []

        station_nodes: list[RouteNode] = [
            RouteNode(
                route_mile=Decimal(str(candidate.route_mile)).quantize(Decimal("0.1")),
                price_per_gallon=Decimal(str(candidate.price_per_gallon)).quantize(Decimal("0.001")),
                station_id=candidate.station_id,
                name=candidate.station_name,
                city=candidate.city,
                state=candidate.state,
                off_route_miles=Decimal(str(candidate.off_route_miles)).quantize(Decimal("0.1")),
            )
            for candidate in candidates
        ]
        terminal = RouteNode(
            route_mile=route_distance_miles.quantize(Decimal("0.1")),
            price_per_gallon=Decimal("0.000"),
            station_id=None,
            name="Destination",
            city="",
            state="",
            off_route_miles=Decimal("0.0"),
            is_terminal=True,
        )

        start_candidates = [node for node in station_nodes if node.route_mile <= CORRIDOR_MILES]
        if not start_candidates:
            if route_distance_miles <= MAX_RANGE_MILES:
                return []
            raise FuelPlanNotFoundError("No fuel station was found near the route start.")

        current_node = min(start_candidates, key=lambda node: (node.price_per_gallon, node.off_route_miles))
        stops: list[FuelStopPlan] = []

        while current_node.route_mile < route_distance_miles:
            reachable_stations = [
                node
                for node in station_nodes
                if (node.route_mile - current_node.route_mile) <= MAX_RANGE_MILES
                and node.route_mile > current_node.route_mile
            ]
            terminal_reachable = (terminal.route_mile - current_node.route_mile) <= MAX_RANGE_MILES

            if terminal_reachable:
                next_node = terminal
            else:
                reachable_stations = [
                    node
                    for node in reachable_stations
                    if (node.route_mile - current_node.route_mile) > Decimal("0")
                ]
                if not reachable_stations:
                    raise FuelPlanNotFoundError(
                        "No fuel station was found within the vehicle range and route corridor."
                    )
                cheaper_station = next(
                    (
                        node
                        for node in reachable_stations
                        if node.price_per_gallon < current_node.price_per_gallon
                    ),
                    None,
                )
                next_node = cheaper_station or max(reachable_stations, key=lambda node: node.route_mile)

            if next_node.route_mile <= current_node.route_mile:
                raise FuelPlanNotFoundError("Fuel planning could not make forward progress along the route.")

            segment_miles = next_node.route_mile - current_node.route_mile
            gallons = (segment_miles / MPG).quantize(Decimal("0.01"))
            cost = (gallons * current_node.price_per_gallon).quantize(Decimal("0.01"))

            if gallons > Decimal("0.00"):
                stops.append(
                    FuelStopPlan(
                        station_id=current_node.station_id or 0,
                        name=current_node.name,
                        city=current_node.city,
                        state=current_node.state,
                        price_per_gallon=current_node.price_per_gallon,
                        route_mile=current_node.route_mile,
                        off_route_miles=current_node.off_route_miles,
                        gallons_purchased=gallons,
                        cost=cost,
                    )
                )

            if next_node.is_terminal:
                break

            current_node = next_node

        return stops
