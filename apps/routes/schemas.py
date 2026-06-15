from pydantic import BaseModel, ConfigDict, Field


class LocationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str
    latitude: float
    longitude: float


class RouteSummarySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    distance_miles: float = Field(ge=0)
    estimated_duration_minutes: float = Field(ge=0)
    fuel_required_gallons: float = Field(ge=0)
    estimated_total_cost: float = Field(ge=0)


class RoutePreviewSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    coordinate_count: int = Field(ge=0)
    start: list[float] | None = None
    end: list[float] | None = None


class FuelStopSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    station_id: int
    name: str
    city: str
    state: str
    price_per_gallon: float
    route_mile: float
    off_route_miles: float
    gallons_purchased: float
    cost: float


class AssumptionsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_range_miles: int
    fuel_efficiency_mpg: int
    route_corridor_miles: int
    fuel_pricing_model: str
    pricing_source: str


class FuelPlanResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: str
    finish: str
    start_location: LocationSchema
    finish_location: LocationSchema
    route_summary: RouteSummarySchema
    route_geometry_preview: RoutePreviewSchema
    fuel_stops: list[FuelStopSchema]
    assumptions: AssumptionsSchema
    notes: list[str]
    route_geometry: dict | None = None
