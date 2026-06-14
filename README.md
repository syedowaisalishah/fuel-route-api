# Fuel Route API

Backend API for planning a U.S. driving route and estimating cost-aware fuel stops using Django, Django REST Framework, OSRM routing, Nominatim geocoding, and local fuel-price data.

## Tech Stack

- Python 3.12
- Django 5.2
- Django REST Framework
- SQLite for local development
- Nominatim for geocoding
- OSRM for routing
- Django local memory cache for repeat geocode/route requests

## Project Layout

- `config/` for project settings, URLs, ASGI, and WSGI
- `apps/routes/` for the route-planning domain app
- `apps/routes/services/` for routing, geocoding, importing, geometry, and optimization logic
- `data/` for sample fuel-price CSV data

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment config:

```bash
cp .env.example .env
```

Run migrations:

```bash
python manage.py migrate
```

Load sample fuel prices:

```bash
python manage.py import_fuel_prices data/sample_fuel_prices.csv
```

Start the server:

```bash
python manage.py runserver
```

## Environment

Required local variables:

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

No paid API key is required for the current implementation. For a public/demo submission, set `NOMINATIM_USER_AGENT` to something identifiable, such as a repo URL or contact string.

## Quick Checks

Health check:

```bash
curl http://127.0.0.1:8000/health/
```

API root:

```bash
curl http://127.0.0.1:8000/api/
```

## What This API Does

The core endpoint accepts two U.S. locations, resolves them to coordinates, pulls an actual driving route, and then estimates fuel stops using local fuel prices.

Endpoint:

`POST /api/routes/fuel-plan/`

Example:

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

Response includes:

- resolved start and finish coordinates
- route distance in miles
- total gallons required at 10 MPG
- estimated total cost
- GeoJSON route geometry
- selected fuel stops
- documented assumptions

## External Services

- Geocoding: Nominatim search API
- Routing: OSRM public route service

Both are wrapped behind service classes and cached by Django cache to avoid repeated free API calls for the same request.

## Fuel Data Import

Use the management command to load the provided fuel-price CSV:

`python manage.py import_fuel_prices path/to/fuel_prices.csv`

Dry run:

`python manage.py import_fuel_prices path/to/fuel_prices.csv --dry-run`

## Assumptions

- The vehicle is modeled with a 500-mile maximum range.
- Fuel efficiency is fixed at 10 MPG.
- Stop planning uses route geometry plus a 10-mile corridor around the route.
- Fuel spending is estimated from the refuel stops the planner selects along the route.
- If no route-corridor station data is available, the API falls back to average known station price, or `3.50` if the database is empty.

## Tests

Run the test suite:

```bash
python manage.py test apps.routes.tests
```

Current coverage focuses on:

- request validation and response shape
- CSV import behavior
- route corridor filtering
- cost-aware station selection

## Interview Notes

This project is intentionally structured as a small algorithmic backend service rather than a demo-only CRUD app. The main signal is in:

- route geometry handling
- corridor-based station filtering
- cost-aware stop selection
- cached service boundaries
- tested importer and optimizer logic

## Docker

Build and run:

```bash
docker build -t fuel-route-api .
docker run --env-file .env -p 8000:8000 fuel-route-api
```

## Demo Flow

For a short walkthrough, show:

1. the request in Postman
2. the route geometry and selected stops in the response
3. the importer command
4. the tests passing
