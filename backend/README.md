# BookEase Backend

BookEase is a simple service-booking platform where customers can reserve and book appointments with service providers (such as haircuts, tutoring, or other services).

The backend is a Flask REST API that manages authentication, services, and appointment bookings while preventing double booking through a temporary reservation system.

A **simplified Flask REST API** for the BookEase booking application. This version contains only the functionality required by the class project.

## Setup

1. Copy the example env file and provide real values:
   ```bash
   cp .env.example .env
   # edit .env to set JWT_SECRET_KEY (and DATABASE_URL if needed)
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000` (or the port shown in the terminal).

## Environment variables

- `JWT_SECRET_KEY` – secret used to sign JSON Web Tokens
- `DATABASE_URL` – optional database URI (defaults to SQLite in `instance/bookease.db`)

## Database schema

Four simple tables: `users`, `services`, `bookings`, and `provider_services`. The models in `models.py` reflect this structure.

## Available endpoints

These cover only the required flows.

### Authentication
- `POST /api/auth/register` – register new user
- `POST /api/auth/login` – obtain JWT token

### Services
- `GET /api/services` – list all services (customers see everything)
- `POST /api/services` – provider creates a service
- `PUT /api/services/<id>` – provider updates their service
- `DELETE /api/services/<id>` – provider deletes their service

### Bookings
- `GET /api/bookings` – view your bookings (customers) or your incoming bookings (providers)
- `POST /api/bookings` – book a slot (confirmed immediately)
- `POST /api/bookings/<id>/reserve` – temporarily reserve a slot (expires in 15 min)
- `PUT /api/bookings/<id>/confirm` – convert reservation to confirmed booking
- `PUT /api/bookings/<id>/cancel` – cancel an existing booking

> **Note:** JWT authentication is required for all service/booking routes. Include header:
> ```
> Authorization: Bearer <token>
> ```

## Unique Feature – Temporary Reservation System

BookEase prevents double booking using a temporary reservation system.

When a user selects a time slot, the system reserves it for **15 minutes** before confirmation. During this time:

- Other users cannot reserve or book the same slot.
- The user must confirm the booking before the timer expires.

If the reservation is not confirmed within 15 minutes, the slot becomes available again.

This mechanism prevents race conditions where multiple users try to book the same appointment at the same time.

## Design notes

- Double‑booking is prevented by checking existing confirmed/reserved bookings for a provider.
- The code is intentionally minimal and readable for a university project.
- No advanced features like availability calendars or background cleanup are included.