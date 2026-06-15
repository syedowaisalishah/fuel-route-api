# Remote Backend Django Engineer - AI & Algorithmic Systems Plan

## Goal
Build a Django API that accepts a start and finish location in the USA, finds a route, determines the best fuel stops along the way, and returns the total fuel cost.

The goal is not just to make it work, but to present it like a strong interview submission:
- clean architecture
- fast API responses
- thoughtful optimization logic
- good documentation
- reliable tests

## Problem Restatement
The API should:
- take a start and finish location in the USA
- return the route map
- identify optimal fuel stops along the route
- respect a maximum vehicle range of 500 miles
- use fuel prices from the provided file
- calculate total fuel cost assuming 10 miles per gallon
- use a free external routing/map API efficiently

## Technical Direction
Use:
- latest stable Django
- Django REST Framework
- a free routing API such as OSRM
- local fuel price data loaded into the database
- caching to avoid repeated external calls

## Architecture

### 1. API Layer
Create a single endpoint:

`POST /api/routes/fuel-plan/`

Example request:

```json
{
  "start": "New York, NY",
  "finish": "Chicago, IL"
}
```

Example response:

```json
{
  "distance_miles": 790.4,
  "fuel_required_gallons": 79.04,
  "estimated_total_cost": 271.88,
  "route_geometry": {
    "type": "LineString",
    "coordinates": []
  },
  "fuel_stops": [
    {
      "name": "Station Name",
      "city": "Somewhere",
      "state": "PA",
      "price_per_gallon": 3.39,
      "route_mile": 247.2,
      "gallons": 32.4,
      "cost": 109.84,
      "coordinates": {
        "lat": 40.1,
        "lng": -79.2
      }
    }
  ]
}
```

### 2. Data Model
Store fuel stations locally with fields like:
- name
- address
- city
- state
- latitude
- longitude
- fuel price

Add indexes for:
- coordinates
- price
- route-related lookups if useful

### 3. Fuel File Import
Build a management command to import the attached fuel price file.

Command example:

`python manage.py import_fuel_prices fuel_prices.csv`

If geocoding is needed for stations, do it once during import, not during route calculation.

### 4. Routing Service
Use one external routing call for a route between start and finish.

Prefer a routing API that can return:
- route geometry
- route distance
- route duration

Cache route results by normalized start and finish input so repeated requests are fast.

### 5. Route Corridor Filtering
Do not inspect every station in the database.

Instead:
- find stations near the route geometry
- calculate each candidate station's distance from the route
- keep only stations inside a practical corridor, such as 5 to 10 miles from the route

This makes the system faster and makes the logic look more deliberate.

### 6. Fuel Stop Optimization
Treat the route as an ordered path from start to finish.

Use the following assumptions:
- vehicle range: 500 miles
- fuel efficiency: 10 miles per gallon
- tank capacity equivalent: 50 gallons

Recommended strategy:
- sort candidate stations by their position along the route
- for each point, look ahead within reachable range
- prefer cheaper future stations when they are reachable
- otherwise stop where needed to stay within range

This is better than simply choosing the cheapest station every 500 miles.

### 7. Cost Calculation
Calculate fuel usage and cost using:

- `gallons_needed = miles_traveled / 10`
- `stop_cost = gallons_bought * station_price`

Return:
- total fuel used
- total fuel cost
- stop-by-stop fuel purchase details

State the fuel assumption clearly in the README, for example:
- the vehicle starts empty
- or the vehicle starts with a full tank

Pick one and stay consistent.

## Performance Strategy
The API should feel fast.

Use these practices:
- one external route API call per unique request
- database-backed fuel station lookup
- cached route results
- corridor filtering before optimization
- efficient data structures and indexed queries

If you can, include timing in logs so you can explain performance during the Loom demo.

## Testing Strategy
Cover the important logic with tests:
- route request validation
- fuel cost math
- range constraints
- stop selection logic
- no reachable station edge cases
- external API mocking

The tests should show that the solution is reliable, not just functional.

## Files and Modules
A clean structure could look like this:

- `routes/`
- `services/routing_service.py`
- `services/geocoding_service.py`
- `services/fuel_station_service.py`
- `services/optimizer.py`
- `management/commands/import_fuel_prices.py`
- `tests/`

## How to Stand Out
To make this feel like a strong interview submission, add these extras:

- OpenAPI or Swagger docs
- `.env.example`
- Docker support
- a strong README
- clear assumptions section
- example API requests and responses
- short explanation of the optimization logic
- caching strategy explanation
- test instructions

The strongest angle is to present this as a constrained optimization problem, not just a Django endpoint.

## 3-Day Execution Plan

### Day 1
- set up Django and DRF
- define station model
- create import command
- load fuel data
- integrate route lookup
- return a basic route response

### Day 2
- implement corridor filtering
- build optimization logic
- calculate fuel cost
- add caching
- write unit tests for the core logic

### Day 3
- polish API response
- add docs and README
- verify edge cases
- run demo scenarios
- record the Loom walkthrough

## Loom Demo Flow
Keep the video under 5 minutes.

Suggested flow:
1. show the request in Postman
2. show the response with route and fuel stops
3. explain the route call and caching
4. explain the optimization logic
5. show tests passing

## Final Submission Checklist
- code pushed to repo
- README updated
- tests included
- API documented
- sample request and response added
- Loom video recorded

## Short Positioning Statement
This project should be described as:

> A Django-based route optimization API that combines external routing data, local fuel pricing, and cost-aware stop planning to generate efficient fuel-up recommendations along a U.S. route.

