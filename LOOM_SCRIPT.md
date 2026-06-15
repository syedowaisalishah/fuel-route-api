# Loom Video Script - Fuel Route API

Target length: 4 to 5 minutes.

## Before Recording

Open these tabs/windows before starting:

1. Postman
2. Browser: `http://127.0.0.1:8000/api/docs/`
3. Code editor with these files ready:
   - `README.md`
   - `apps/routes/views.py`
   - `apps/routes/serializers.py`
   - `apps/routes/services/fuel_plan_service.py`
   - `apps/routes/services/geocoding_service.py`
   - `apps/routes/services/routing_service.py`
   - `apps/routes/services/optimizer.py`
   - `apps/routes/management/commands/import_fuel_prices.py`
   - `apps/routes/schemas.py`
   - `apps/routes/tests/test_fuel_plan_api.py`

Run the app before recording:

```bash
docker compose up --build
```

Or local:

```bash
python manage.py migrate
python manage.py import_fuel_prices data/sample_fuel_prices.csv
python manage.py runserver
```

## 0:00 - 0:30 Introduction

Hi, my name is Nabeel. In this project I built a Django 5.2 backend API for the fuel route planning assignment.

The requirement was to accept a start and finish location inside the USA, find a driving route, recommend cost-effective fuel stops along that route, respect a 500-mile vehicle range, and return the total fuel cost assuming 10 miles per gallon.

I treated this as a backend routing and optimization problem, not just a simple CRUD API. The implementation uses Django REST Framework, OSRM for routing, Nominatim for geocoding, local fuel-price data, caching, typed internal schemas with Pydantic, Docker, tests, and Swagger documentation.

## 0:30 - 1:30 Postman Demo

Now I will show the API working in Postman.

I am sending a POST request to:

`/api/routes/fuel-plan/`

The request body is:

```json
{
  "start": "Austin, TX",
  "finish": "Dallas, TX"
}
```

This returns a clean response for the demo.

The important result is inside `route_summary`. Here you can see:

- the total distance in miles
- estimated duration
- fuel required in gallons
- estimated total cost

The response also includes resolved start and finish coordinates, selected fuel stops, route preview, assumptions, and notes.

I made the default response compact because full route geometry can contain hundreds or thousands of coordinate points, which is hard to read in Postman. If the client needs the full map geometry, it can send:

```json
{
  "start": "Austin, TX",
  "finish": "Dallas, TX",
  "include_geometry": true
}
```

That returns the full GeoJSON route geometry for displaying the route on a map.

## 1:30 - 2:00 Swagger/OpenAPI

I also added Swagger documentation.

Here I am opening:

`/api/docs/`

This gives a browser-based API contract. A reviewer can inspect the endpoint, request body, and response structure without reading the code first.

This is useful for handoff and makes the project easier to test and understand.

## 2:00 - 2:40 Project Structure

Now I will quickly explain the code structure.

The project uses a clean Django layout.

`config/` contains the project-level settings, URL routing, ASGI, and WSGI files.

`apps/routes/` contains the actual route-planning domain app.

Inside the app, I separated responsibilities:

- `models.py` stores fuel station data
- `serializers.py` validates API request input
- `views.py` handles the HTTP request and maps errors to correct status codes
- `services/` contains the business logic
- `management/commands/` contains the fuel-price import command
- `tests/` contains API and service tests

This structure keeps the view thin and puts the core behavior into reusable service classes.

## 2:40 - 3:45 Code Walkthrough

Open `apps/routes/views.py`.

This file handles the API endpoint. It validates the request using the serializer, calls the fuel plan service, and returns the response.

It also uses meaningful HTTP status codes:

- `200` for success
- `400` for invalid input
- `404` when a location or route cannot be found
- `503` when an upstream service is unavailable
- `504` when an upstream service times out

This makes the API behavior clearer than returning `200` for everything.

Open `apps/routes/services/fuel_plan_service.py`.

This is the orchestration layer. It resolves the start and finish locations, gets the route, calculates distance and gallons, asks the optimizer for fuel stops, and builds the final response.

Open `apps/routes/services/geocoding_service.py`.

This service uses Nominatim to convert location text into coordinates. The result is cached, so repeated requests do not keep hitting the external API.

Open `apps/routes/services/routing_service.py`.

This service uses OSRM to get the driving route. I request the full route geometry once, cache the result, and reuse it for repeat requests.

Open `apps/routes/services/optimizer.py`.

This is the algorithmic part. It filters fuel stations near the route corridor, respects the 500-mile range, and chooses fuel stops based on route position and fuel price.

Open `apps/routes/schemas.py`.

I used Pydantic here for internal response schemas. DRF serializers still handle request validation, but Pydantic gives typed internal response contracts for the service layer.

Open `apps/routes/management/commands/import_fuel_prices.py`.

This custom Django command imports the fuel-price CSV into the database:

```bash
python manage.py import_fuel_prices data/sample_fuel_prices.csv
```

It also supports dry run mode.

## 3:45 - 4:20 Testing and Reliability

Open `apps/routes/tests/`.

The tests cover:

- API response shape
- invalid request validation
- missing location and timeout status codes
- fuel CSV import
- optimizer behavior
- provider caching

I can run:

```bash
python manage.py test apps.routes.tests
```

This gives confidence that the main API behavior, error handling, and algorithm pieces are working.

## 4:20 - 4:50 Standout Features

To make the project stronger than a basic submission, I added:

- Docker Compose, so the reviewer can run it with one command
- Swagger/OpenAPI docs
- Pydantic response schemas
- service-layer architecture
- external API caching
- meaningful HTTP status codes
- compact default response with optional full route geometry
- custom fuel-price import command
- tests for important behavior

The route API call is intentionally limited. The system geocodes the locations, fetches the route, and then does station filtering and optimization locally using database fuel prices.

## 4:50 - 5:00 Closing

In summary, this is a Django backend API that combines external routing data, local fuel-price data, and cost-aware stop planning to estimate fuel stops and trip cost.

I focused on clean architecture, fast repeated requests through caching, clear API behavior, and a response format that is easy to demo and easy for another engineer to consume.

Thank you.

## Shorter Backup Script

If you are running out of time, say this:

I built a Django 5.2 API that accepts a start and finish location in the USA, geocodes them with Nominatim, gets a driving route from OSRM, filters local fuel stations near the route, and returns cost-aware fuel stops plus total fuel cost at 10 miles per gallon.

The app uses a clean `config/` and `apps/` structure, DRF for request validation, Pydantic for internal response schemas, caching for external provider calls, Docker Compose for simple setup, Swagger docs for API review, and tests for the API, importer, optimizer, and cache behavior.

For the demo, the default response is compact and readable. If the client needs the full route geometry for a map, it can send `include_geometry: true`.

## Good Interview Phrases

- I kept the API response compact by default because full GeoJSON route geometry is noisy in Postman.
- I still support full geometry with `include_geometry: true`.
- I used DRF serializers for request validation because that is idiomatic Django.
- I used Pydantic for internal typed response contracts.
- I separated provider calls, optimization, importing, and API handling into services.
- I used caching to avoid repeated external API calls.
- I mapped errors to meaningful HTTP status codes instead of returning `200` or `400` for every case.
- I added Docker Compose and Swagger so the project is easy to run and easy to review.

## Files to Mention

- `README.md`: setup, Docker, API usage, assumptions
- `config/settings.py`: Django, DRF, Swagger, cache, provider config
- `config/urls.py`: health, API routes, Swagger docs
- `apps/routes/views.py`: API endpoint and status code mapping
- `apps/routes/serializers.py`: request validation
- `apps/routes/schemas.py`: Pydantic response schemas
- `apps/routes/services/fuel_plan_service.py`: main orchestration
- `apps/routes/services/geocoding_service.py`: Nominatim integration and cache
- `apps/routes/services/routing_service.py`: OSRM integration and cache
- `apps/routes/services/optimizer.py`: route corridor and fuel-stop selection
- `apps/routes/management/commands/import_fuel_prices.py`: CSV import command
- `apps/routes/tests/`: behavior tests

## Exact Code Lines to Show

You do not need to explain every line. Open only these areas and say the short explanation.

### 1. `apps/routes/views.py`

Show lines `29-49`.

Say:

This is the API controller. It validates the request, calls the service layer, and maps different failures to correct HTTP status codes. Success returns `200`, validation errors are handled by DRF as `400`, missing location or route returns `404`, upstream timeout returns `504`, and upstream unavailable returns `503`.

Important lines:

- `31-32`: request validation with DRF serializer
- `35-39`: call the business service
- `40-47`: meaningful error status codes
- `49`: successful response

### 2. `apps/routes/serializers.py`

Show lines `4-12`.

Say:

This serializer validates the request body. It requires `start` and `finish`, and supports optional `include_geometry`. I also reject same start and finish values early.

Important lines:

- `5-7`: request fields
- `9-12`: custom validation

### 3. `apps/routes/services/fuel_plan_service.py`

Show lines `19-33`.

Say:

This is the orchestration service. It geocodes the start and finish, calls the routing service once, calculates distance and required gallons, and then asks the optimizer for fuel stops.

Important lines:

- `21-22`: geocode start and finish
- `23-28`: fetch the route
- `30-31`: calculate miles and fuel gallons
- `33`: call the optimizer

Then show lines `41-93`.

Say:

This section builds the final response using Pydantic schemas. The default response is compact for Postman and Loom, and full geometry is only included when `include_geometry` is true.

Important lines:

- `41`: start Pydantic response schema
- `54-61`: route summary
- `62`: compact route preview
- `63-76`: fuel stops
- `77-83`: assumptions
- `90-91`: optional full geometry
- `93`: final validated response dictionary

### 4. `apps/routes/services/geocoding_service.py`

Show lines `38-80`.

Say:

This service uses Nominatim to convert a location like Austin, Texas into coordinates. I cache the result so repeated requests do not keep hitting the external provider.

Important lines:

- `40-43`: cache lookup
- `45-56`: Nominatim request setup
- `58-66`: timeout and provider failure handling
- `68-69`: location-not-found handling
- `72-80`: return and cache resolved coordinates

### 5. `apps/routes/services/routing_service.py`

Show lines `35-68`.

Say:

This service uses OSRM to get the driving route. It requests GeoJSON geometry and route distance, then caches the result. This helps satisfy the requirement to avoid excessive map/routing API calls.

Important lines:

- `37-40`: route cache lookup
- `42-46`: OSRM route request
- `48-56`: timeout and provider failure handling
- `58-59`: no-route handling
- `61-68`: normalize and cache route response

### 6. `apps/routes/services/optimizer.py`

Show lines `15-17`.

Say:

These constants model the assignment rules: 500-mile maximum range, 10 miles per gallon, and a 10-mile route corridor for fuel stations.

Show lines `49-62`.

Say:

This is the optimizer entry point. It takes the route geometry, finds station candidates near the route, and returns selected fuel stops plus total cost.

Show lines `64-96`.

Say:

This collects stations near the route. Instead of checking all stations blindly in the final logic, I calculate where each station is near the route and filter by corridor distance.

Show lines `125-170`.

Say:

This is the stop-selection logic. It starts near the route start, checks reachable stations within 500 miles, decides whether the destination is reachable, and calculates gallons and cost for each leg.

Important lines:

- `125-131`: choose a starting station near the route start
- `134-141`: find reachable stations and destination
- `151-163`: handle no station and choose next reachable station
- `168-170`: calculate gallons and cost

### 7. `apps/routes/schemas.py`

Show lines `12-18` and `54-66`.

Say:

I used Pydantic for internal response schemas. DRF handles request validation, while Pydantic gives the service layer a typed response contract.

Important lines:

- `12-18`: typed route summary
- `54-66`: full API response schema

### 8. `apps/routes/management/commands/import_fuel_prices.py`

Show lines `6-35`.

Say:

This is a custom Django management command for importing fuel price data from a CSV file. It also supports dry run mode, which is useful for checking files before writing to the database.

Important lines:

- `9-11`: command arguments
- `18-21`: import execution and missing-file handling
- `23-29`: dry run output
- `31-35`: success output

### 9. `config/urls.py`

You do not need to explain line by line. Just show it briefly.

Say:

This file wires the main project URLs: health check, API routes, OpenAPI schema, and Swagger UI.

### 10. `config/settings.py`

You do not need to explain line by line.

Say:

This file configures Django, DRF, Swagger, caching, database, and external provider settings from environment variables.

### 11. `apps/routes/tests/`

You do not need to open every test file. Show the folder or one test file briefly.

Say:

The tests cover API response shape, validation, status codes, import behavior, optimizer behavior, and provider caching.

