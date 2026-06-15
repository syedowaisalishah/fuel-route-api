# Fuel Route API

A Django 5.2 backend API for planning a U.S. driving route, selecting cost-aware fuel stops, and estimating trip fuel cost.

The assignment asks for an API that accepts a start and finish location in the USA, returns a route, recommends optimal fuel-up locations based on fuel prices, respects a 500-mile vehicle range, and calculates total fuel spend at 10 MPG.

This implementation treats the task as a small routing and optimization system, not a CRUD app. The route comes from live routing data, fuel prices come from the provided assessment CSV, and the backend keeps the response readable for review while still supporting full map geometry when needed.

## Highlights

- Real route lookup using OSRM
- U.S. location geocoding using Nominatim
- Direct support for the provided assessment fuel-price CSV
- Local fuel-price import through a custom Django management command
- Route-corridor station filtering
- Cost-aware fuel stop selection
- Compact default API response for readable demos
- Optional full GeoJSON route geometry with `include_geometry`
- Pydantic response schemas for typed service-layer contracts
- Proper HTTP status codes for validation, not-found, provider failure, and timeout cases
- Cached geocoding and routing calls to avoid repeated external API requests
- Swagger/OpenAPI docs
- Docker Compose setup
- Tests for API behavior, importer, optimizer, and provider cache

## Assessment Data Support

The project is wired to use:

```text
data/fuel-prices-for-be-assessment.csv
```

That file contains truckstop pricing data with columns such as:

- `Truckstop Name`
- `Address`
- `City`
- `State`
- `Retail Price`

The assessment file does not include latitude and longitude. The importer stores the provided station identity and price data exactly as local fuel-price records. When coordinates are available, the optimizer can place stations along the route corridor. When coordinates are not available, the API still uses the imported price data for cost estimation instead of ignoring the provided file.

This keeps the implementation honest about the dataset while still satisfying the assignment requirement to use the attached fuel-price data.

## Quick Start With Docker

```bash
cp .env.example .env
docker compose up --build
```

The container will:

- install dependencies
- run database migrations
- import `data/fuel-prices-for-be-assessment.csv`
- start Django at `http://127.0.0.1:8000`

Useful URLs:

- Health: `http://127.0.0.1:8000/health/`
- API root: `http://127.0.0.1:8000/api/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py import_fuel_prices data/fuel-prices-for-be-assessment.csv
python manage.py runserver
```

## API Usage

Endpoint:

```http
POST /api/routes/fuel-plan/
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/routes/fuel-plan/ \
  -H "Content-Type: application/json" \
  -d '{"start": "Austin, TX", "finish": "Dallas, TX"}'
```

Request body:

```json
{
  "start": "Austin, TX",
  "finish": "Dallas, TX"
}
```

Compact response shape:

```json
{
  "start": "Austin, TX",
  "finish": "Dallas, TX",
  "start_location": {
    "display_name": "Austin, Travis County, Texas, United States",
    "latitude": 30.2711286,
    "longitude": -97.7436995
  },
  "finish_location": {
    "display_name": "Dallas, Dallas County, Texas, United States",
    "latitude": 32.7762719,
    "longitude": -96.7968559
  },
  "route_summary": {
    "distance_miles": 195.2,
    "estimated_duration_minutes": 178.4,
    "fuel_required_gallons": 19.52,
    "estimated_total_cost": 68.06
  },
  "route_geometry_preview": {
    "type": "LineString",
    "coordinate_count": 1200,
    "start": [-97.743783, 30.270908],
    "end": [-96.796942, 32.776304]
  },
  "fuel_stops": [],
  "assumptions": {
    "vehicle_range_miles": 500,
    "fuel_efficiency_mpg": 10,
    "route_corridor_miles": 10,
    "fuel_pricing_model": "route-hop refuel estimate using station prices on the selected path",
    "pricing_source": "average_or_default_price"
  }
}
```

To include the full GeoJSON route geometry:

```json
{
  "start": "Austin, TX",
  "finish": "Dallas, TX",
  "include_geometry": true
}
```

## HTTP Status Codes

- `200 OK`: fuel plan generated
- `400 Bad Request`: invalid request body, for example same start and finish
- `404 Not Found`: location or route could not be found
- `503 Service Unavailable`: upstream geocoding or routing service unavailable
- `504 Gateway Timeout`: upstream geocoding or routing service timed out

This keeps API behavior explicit and easier to debug than returning only `200` or `400`.

## Fuel Data Import

Load fuel prices:

```bash
python manage.py import_fuel_prices data/fuel-prices-for-be-assessment.csv
```

Dry run without writing:

```bash
python manage.py import_fuel_prices data/fuel-prices-for-be-assessment.csv --dry-run
```

The importer accepts common CSV headers such as:

- `Truckstop Name`
- `station_name`, `name`, `brand`
- `Address`
- `address`, `street`, `street_address`
- `City`
- `city`, `town`
- `State`
- `state`, `region`
- `lat`, `latitude`
- `lon`, `lng`, `long`, `longitude`
- `Retail Price`
- `price`, `gas_price`, `price_per_gallon`

## Architecture

```text
config/
  settings.py        Project settings, DRF, Swagger, cache, provider config
  urls.py            Project URL routing

apps/routes/
  models.py          FuelStation database model
  serializers.py     DRF request validation
  schemas.py         Pydantic response schemas
  views.py           API controller and HTTP status mapping
  services/
    fuel_plan_service.py       Main orchestration
    geocoding_service.py       Nominatim integration and cache
    routing_service.py         OSRM integration and cache
    optimizer.py               Route corridor and fuel-stop logic
    geometry_utils.py          Distance and route helpers
    fuel_station_importer.py   CSV parsing and import
  management/commands/
    import_fuel_prices.py      Custom import command
  tests/             API, importer, optimizer, and provider cache tests
```

## Algorithm Summary

The fuel planning flow is:

1. Geocode start and finish locations inside the USA.
2. Fetch one driving route from OSRM with GeoJSON geometry.
3. Load fuel prices from the local database.
4. Use station coordinates for corridor-based stop placement when coordinates are present.
5. Use imported assessment prices for cost estimation when coordinate-level placement is not available.
6. Respect a 500-mile maximum vehicle range.
7. Estimate gallons using `miles / 10`.
8. Estimate cost using selected or fallback station prices.
9. Return a compact response for API consumers, with optional full geometry for maps.

## External Services

- Nominatim: geocoding start and finish text into coordinates
- OSRM: route distance, duration, and GeoJSON geometry

Both service calls are cached with Django cache. This improves repeated demo speed and reduces unnecessary external API calls.

No paid API key is required.

## Environment Variables

```bash
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,testserver
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org/search
NOMINATIM_USER_AGENT=fuel-route-api/0.1
OSRM_BASE_URL=https://router.project-osrm.org
EXTERNAL_API_TIMEOUT_SECONDS=10
ROUTE_CACHE_TIMEOUT_SECONDS=86400
GEOCODING_CACHE_TIMEOUT_SECONDS=86400
```

For a public submission, set `NOMINATIM_USER_AGENT` to something identifiable, such as a repository URL or contact string.

## Tests

```bash
python manage.py test apps.routes.tests
```

The test suite covers:

- successful fuel-plan response shape
- optional full geometry
- invalid request validation
- `404` missing-location behavior
- `504` timeout behavior
- CSV importer dry-run behavior
- optimizer candidate selection
- provider caching

## Postman

Import:

- `postman/Fuel Route API.postman_collection.json`
- `postman/Fuel Route API.local.postman_environment.json`

Select the `Fuel Route API Local` environment and run:

- `Health Check`
- `API Root`
- `Fuel Plan`

## Swagger

Open:

```text
http://127.0.0.1:8000/api/docs/
```

Use this during the Loom demo to show the API contract in the browser.

## Loom Guide

The full read-aloud Loom script is in:

```text
LOOM_SCRIPT.md
```

Recommended demo order:

1. Start the app with Docker Compose
2. Show Swagger UI
3. Send the Postman `Fuel Plan` request
4. Explain the compact response and `include_geometry`
5. Walk through `views.py`, `fuel_plan_service.py`, `optimizer.py`, and provider services
6. Run the tests

## Assumptions

- Start and finish must resolve to U.S. locations.
- Vehicle maximum range is 500 miles.
- Fuel efficiency is fixed at 10 MPG.
- Route corridor is 10 miles.
- Fuel prices come from the imported assessment CSV.
- The provided assessment CSV has station address data but no latitude/longitude columns.
- If no coordinate-level route-corridor station data is available, the API falls back to average known imported station price, or `3.50` if the database is empty.

## Why This Stands Out

This project is intentionally built like a small production backend:

- thin API views
- service-layer business logic
- clear data validation boundaries
- typed Pydantic response contracts
- external provider isolation
- cached route/geocode calls
- meaningful HTTP status codes
- Dockerized setup
- Swagger docs
- tests around important behavior

The core engineering choice is to treat route planning as a constrained optimization problem over route geometry and local fuel prices, not just a simple endpoint that returns static data.

## Reviewer Note

The API is designed to be easy to review in a short Loom:

- Docker starts the app and imports the assessment CSV.
- Postman shows the compact fuel-plan response.
- Swagger shows the API contract.
- The code walkthrough can focus on `views.py`, `fuel_plan_service.py`, `optimizer.py`, and the provider services.
