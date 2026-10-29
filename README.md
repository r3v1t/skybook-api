# SkyBook API

REST API for searching flights and booking air tickets, built with **Django REST Framework**, **PostgreSQL** and **Docker**.

It is a Python rewrite and extension of my university Databases course project (a C# desktop app for an air ticket agency).

## Features

- **JWT authentication:** register, log in, refresh token, view your profile
- **Flight search:** filter by origin, destination, date, price range and free seats; search and sort the results
- **Safe booking:** a database transaction with row locking (`SELECT ... FOR UPDATE`) stops two users from buying the same seat
- **Seat map:** `GET /api/flights/{id}/seats/` lists the free seats
- **Ticket cancellation:** a cancelled seat goes back on sale
- **Roles:** staff manage airports, aircraft and flights; users see only their own tickets
- **Sales report (staff):** tickets sold, occupancy % and revenue for each flight
- **OpenAPI / Swagger docs** at `/api/docs/`
- **Tests** for the API and the booking rules, run in GitHub Actions against PostgreSQL

## Tech stack

Python 3.12 · Django 5.2 · Django REST Framework · SimpleJWT · django-filter · drf-spectacular · PostgreSQL 16 · Docker / Docker Compose · Gunicorn · GitHub Actions

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

Then, in a second terminal, add demo data and an admin user:

```bash
docker compose exec web python manage.py seed_demo
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000/api/docs/ for the API docs.

## Run locally without Docker (SQLite)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Set `DATABASE_URL=postgres://user:pass@host:5432/db` to use PostgreSQL instead of SQLite.

## Tests

```bash
python manage.py test
```

## API overview

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | anyone | Create an account |
| POST | `/api/auth/token/` | anyone | Get access and refresh tokens |
| POST | `/api/auth/token/refresh/` | anyone | Refresh the access token |
| GET | `/api/auth/me/` | user | Current user |
| GET | `/api/flights/?origin=WAW&destination=BER&date=2026-11-02&max_price=100&min_seats=2` | anyone | Search flights |
| GET | `/api/flights/{id}/seats/` | anyone | Free seats on a flight |
| POST/PUT/DELETE | `/api/flights/`, `/api/airports/`, `/api/aircraft/` | staff | Manage flights and reference data |
| POST | `/api/tickets/` | user | Book a ticket |
| GET | `/api/tickets/` | user | My tickets (staff: all tickets) |
| POST | `/api/tickets/{id}/cancel/` | user | Cancel a ticket |
| GET | `/api/reports/flights/` | staff | Sales report |

### Example: book a ticket

```bash
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"flight": 1, "seat_number": 12, "passenger_first_name": "Roman", "passenger_last_name": "Popovych", "document_number": "AB123456"}'
```

## Project structure

```
config/      settings and root URLs
accounts/    registration, JWT login, profile
flights/     airports, aircraft, flights, search filters, demo data command
bookings/    tickets, booking service (transactions), sales report
```
