# Garage API Project

A Flask REST API for managing mechanics, service tickets, and mechanic-to-ticket assignments.

## What This Project Does

This API helps model a small auto-service workflow:
- Create, list, update, and delete mechanics.
- Create and list service tickets.
- Assign or remove mechanics from service tickets (many-to-many relationship).

## Tech Stack

- Python 3.14+
- Flask
- Flask-SQLAlchemy
- Marshmallow + Marshmallow-SQLAlchemy
- SQLite (default fallback) or MySQL (`mysql-connector-python`)

## Project Structure

```text
garage-api-project/
  mechanics/
    __init__.py        # App factory + DB configuration + mechanics blueprint setup
    routes.py          # Mechanics endpoints
    schemas.py         # Mechanics serialization/validation
  service_tickets/
    bp.py              # Service tickets blueprint
    routes.py          # Service ticket endpoints
    schemas.py         # Service ticket serialization/validation
  models.py            # SQLAlchemy models + relationships
  run.py               # Main app entrypoint
  requirements.txt
  .env.example
```

## Data Model

### Mechanic
- `id` (int, auto-generated)
- `name` (string, required)
- `email` (string, required, unique)
- `specialty` (string, required)

### ServiceTicket
- `id` (int, auto-generated)
- `vin` (string, required)
- `service_date` (date, required)
- `description` (string, required)
- `customer_id` (int, required)

### Relationship
- A service ticket can have many mechanics.
- A mechanic can be assigned to many service tickets.

## Setup

1. Open a terminal in the project folder:

```bash
cd garage-api-project
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Windows CMD:

```bash
.venv\Scripts\activate.bat
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Copy `.env.example` to `.env` and adjust values if needed.

### Option A: Quick local run (SQLite)
If no complete MySQL config is provided, the app falls back to SQLite automatically:

```env
# leave DATABASE_URL unset
# leave MYSQL_* unset or incomplete
```

### Option B: MySQL
Use either:
- `DATABASE_URL`
- or all `MYSQL_*` values

Example:

```env
MYSQL_USER=garage_user
MYSQL_PASSWORD=your_real_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=mechanic_library_db
```

## Run the API

Recommended entrypoint:

```bash
python run.py
```

Server URL:
- `http://127.0.0.1:5000`

## API Endpoints

### Mechanics

- `POST /mechanics/` - Create a mechanic
- `GET /mechanics/` - List mechanics
- `PUT /mechanics/<id>` - Update a mechanic
- `DELETE /mechanics/<id>` - Delete a mechanic

Create mechanic body example:

```json
{
  "name": "Alex Rivera",
  "email": "alex.rivera@example.com",
  "specialty": "Transmission"
}
```

### Service Tickets

- `POST /service-tickets/` - Create a service ticket
- `GET /service-tickets/` - List service tickets
- `PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>` - Assign mechanic
- `PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>` - Remove mechanic

Create service ticket body example:

```json
{
  "vin": "1HGCM82633A123456",
  "service_date": "2026-07-17",
  "description": "Brake inspection",
  "customer_id": 42
}
```

## Quick Demo (PowerShell)

Create a mechanic:

```powershell
$body = '{"name":"Test Mechanic","email":"test.mechanic@example.com","specialty":"Brakes"}'
Invoke-WebRequest -Uri 'http://127.0.0.1:5000/mechanics/' -Method Post -ContentType 'application/json' -Body $body
```

Create a service ticket:

```powershell
$body = '{"vin":"1HGCM82633A123456","service_date":"2026-07-17","description":"Oil change","customer_id":123}'
Invoke-WebRequest -Uri 'http://127.0.0.1:5000/service-tickets/' -Method Post -ContentType 'application/json' -Body $body
```

Assign mechanic `1` to ticket `1`:

```powershell
Invoke-WebRequest -Uri 'http://127.0.0.1:5000/service-tickets/1/assign-mechanic/1' -Method Put
```

## Postman Test Cases (Short)

Set a collection variable:
- `base_url = http://127.0.0.1:5000`

Run these requests in order:

1. Create mechanic (happy path)
- Method/URL: `POST {{base_url}}/mechanics/`
- Body:

```json
{
  "name": "Postman Mechanic",
  "email": "postman.mechanic@example.com",
  "specialty": "Engine"
}
```

- Expected: `201 Created`

2. Create duplicate mechanic (error path)
- Method/URL: `POST {{base_url}}/mechanics/`
- Body: same as test 1
- Expected: `409 Conflict`

3. List mechanics
- Method/URL: `GET {{base_url}}/mechanics/`
- Expected: `200 OK` and array contains `postman.mechanic@example.com`

4. Create service ticket (happy path)
- Method/URL: `POST {{base_url}}/service-tickets/`
- Body:

```json
{
  "vin": "1HGCM82633A654321",
  "service_date": "2026-07-17",
  "description": "Battery replacement",
  "customer_id": 501
}
```

- Expected: `201 Created`

5. Assign mechanic to ticket
- Method/URL: `PUT {{base_url}}/service-tickets/1/assign-mechanic/1`
- Expected: `200 OK`

6. Remove mechanic from ticket
- Method/URL: `PUT {{base_url}}/service-tickets/1/remove-mechanic/1`
- Expected: `200 OK`

7. Assign with missing entities (error path)
- Method/URL: `PUT {{base_url}}/service-tickets/999/assign-mechanic/999`
- Expected: `404 Not Found`

## Error Behavior Notes

- `409 Conflict` is returned for unique constraint violations (for example, duplicate mechanic email).
- `404 Not Found` is returned when target mechanic or ticket records do not exist.
- Validation errors return `400` with schema details.

## Notes for Development

- Database tables are auto-created on app startup (`db.create_all()`).
- Primary keys (`id`) are output-only in schema definitions.
- Running `python run.py` is preferred over launching route files directly.
