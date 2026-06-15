from decimal import Decimal

from django.db.models import Avg

from apps.routes.models import FuelStation
from apps.routes.schemas import (
    AssumptionsSchema,
    FuelPlanResponseSchema,
    FuelStopSchema,
    LocationSchema,
    RoutePreviewSchema,
    RouteSummarySchema,
)
from apps.routes.services.geocoding_service import GeocodingService
from apps.routes.services.optimizer import FuelPlanNotFoundError, FuelRouteOptimizer, MPG
from apps.routes.services.routing_service import RoutingService


class FuelPlanService:
    def build_plan(self, start: str, finish: str, include_geometry: bool = False) -> dict:
        start_location = GeocodingService().resolve_us_location(start)
        finish_location = GeocodingService().resolve_us_location(finish)
        route = RoutingService().get_route(
            start_lat=start_location.latitude,
            start_lng=start_location.longitude,
            finish_lat=finish_location.latitude,
            finish_lng=finish_location.longitude,
        )

        distance_miles = Decimal(str(route.distance_meters / 1609.344)).quantize(Decimal("0.1"))
        fuel_required_gallons = (distance_miles / MPG).quantize(Decimal("0.01"))
        try:
            stop_plans, stop_cost = FuelRouteOptimizer().build_stop_plan(route.geometry, Decimal(str(distance_miles)))
            total_cost = stop_cost if stop_plans else self._estimate_cost(distance_miles)
            pricing_source = "selected_fuel_stops" if stop_plans else "average_or_default_price"
        except FuelPlanNotFoundError:
            stop_plans = []
            total_cost = self._estimate_cost(distance_miles)
            pricing_source = "fallback_average_or_default_price"

        payload = FuelPlanResponseSchema(
            start=start,
            finish=finish,
            start_location=LocationSchema(
                display_name=start_location.display_name,
                latitude=start_location.latitude,
                longitude=start_location.longitude,
            ),
            finish_location=LocationSchema(
                display_name=finish_location.display_name,
                latitude=finish_location.latitude,
                longitude=finish_location.longitude,
            ),
            route_summary=RouteSummarySchema(
                distance_miles=float(distance_miles),
                estimated_duration_minutes=float(
                    Decimal(str(route.duration_seconds / 60)).quantize(Decimal("0.1"))
                ),
                fuel_required_gallons=float(fuel_required_gallons),
                estimated_total_cost=float(total_cost),
            ),
            route_geometry_preview=RoutePreviewSchema(**self._preview_geometry(route.geometry)),
            fuel_stops=[
                FuelStopSchema(
                    station_id=stop.station_id,
                    name=stop.name,
                    city=stop.city,
                    state=stop.state,
                    price_per_gallon=float(stop.price_per_gallon),
                    route_mile=float(stop.route_mile),
                    off_route_miles=float(stop.off_route_miles),
                    gallons_purchased=float(stop.gallons_purchased),
                    cost=float(stop.cost),
                )
                for stop in stop_plans
            ],
            assumptions=AssumptionsSchema(
                vehicle_range_miles=500,
                fuel_efficiency_mpg=10,
                route_corridor_miles=10,
                fuel_pricing_model="route-hop refuel estimate using station prices on the selected path",
                pricing_source=pricing_source,
            ),
            notes=[
                "Route is fetched from a live routing service.",
                "Fuel-stop optimization uses the route geometry corridor and local fuel prices.",
            ],
        )

        if include_geometry:
            payload.route_geometry = route.geometry

        return payload.model_dump(mode="python", exclude_none=True)

    def _estimate_cost(self, distance_miles: Decimal) -> Decimal:
        gallons = distance_miles / MPG
        average_price = FuelStation.objects.aggregate(avg_price=Avg("price_per_gallon"))["avg_price"]
        price = Decimal(str(average_price)) if average_price is not None else Decimal("3.50")
        return (gallons * price).quantize(Decimal("0.01"))

    def _preview_geometry(self, geometry: dict) -> dict:
        coordinates = geometry.get("coordinates") or []
        preview = {
            "type": geometry.get("type", "LineString"),
            "coordinate_count": len(coordinates),
        }
        if coordinates:
            preview["start"] = coordinates[0]
            preview["end"] = coordinates[-1]
        return preview
