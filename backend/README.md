# BookEase Backend

BookEase is a Flask REST API for a student service-booking app. It supports customers, providers, and admins; service browsing by category; provider schedules; booking, reservation, cancellation, rescheduling, feedback, and basic admin management.

The backend is intentionally small for the class project, but it covers the required proposal features.

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:

   ```bash
   cp .env.example .env
   ```

   Make sure `.env` has a JWT secret:

   ```bash
   JWT_SECRET_KEY=dev-secret
   ```

4. Run the backend:

   ```bash
   python app.py
   ```

The API runs at:

```text
http://localhost:5001
```

The SQLite database is created automatically at:

```text
backend/instance/bookease.db
```

## Authentication

Protected routes require this header:

```text
Authorization: Bearer <token>
```

Use `POST /api/auth/login` to get the token.

## First Admin

Normal registration only allows `customer` and `provider` accounts. To create the first admin, use the one-time bootstrap route:

```bash
curl -X POST http://localhost:5001/api/auth/bootstrap-admin \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@bookease.com","password":"admin123"}'
```

After one admin exists, this route returns an error and cannot create another admin.

## Main Rules

- Customers can book, reserve, cancel, reschedule, view booking history, and leave feedback.
- Providers can create services, manage only their own services, set schedules, and view incoming bookings.
- Admins can create, update, and delete any service, manage users, view bookings, and manage cancellation policies.
- Service duration must be `15`, `30`, or `60` minutes.
- A customer can have at most two active bookings.
- A provider cannot be double-booked.
- Bookings and reservations must fit inside the provider's active schedule.
- Feedback can only be left by the customer who made the booking, for the matching service, after the session has ended.

## Availability

The availability endpoint returns the provider's active schedule and existing booked/reserved slots:

```text
GET /api/availability/<provider_id>?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

Important demo wording:

```text
The backend returns schedule windows and booked times. The frontend calculates and displays the open time slots.
```

Do not say the backend calculates every available slot.

## Temporary Reservation System

BookEase includes a temporary reservation flow to prevent double booking while a customer is completing a booking.

Use:

```text
POST /api/bookings/reserve
```

This creates a `reserved` booking for 15 minutes. During that time, other users cannot book or reserve the same provider time. A background cleanup job deletes expired reservations every 5 minutes.

To finalize the reservation:

```text
PUT /api/bookings/<booking_id>/confirm
```

## Database Models

The backend currently uses these models:

- `User`
- `Service`
- `Booking`
- `ProviderService`
- `Feedback`
- `ProviderSchedule`
- `CancellationPolicy`

## API Routes

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/bootstrap-admin`

### Services

- `GET /api/services`
- `GET /api/services?category=<category>`
- `POST /api/services`
- `PUT /api/services/<service_id>`
- `DELETE /api/services/<service_id>`

### Bookings

- `GET /api/bookings`
- `POST /api/bookings`
- `POST /api/bookings/reserve`
- `PUT /api/bookings/<booking_id>/confirm`
- `PUT /api/bookings/<booking_id>/cancel`
- `PUT /api/bookings/<booking_id>/reschedule`
- `GET /api/bookings/history`
- `GET /api/bookings/upcoming`

### Admin

- `GET /api/admin/users`
- `GET /api/admin/bookings`
- `PUT /api/admin/users/<user_id>/roles`

### Profile

- `GET /api/profile`
- `PUT /api/profile`

### Feedback

- `POST /api/feedback`
- `GET /api/feedback/service/<service_id>`

### Provider Schedule

- `GET /api/schedule`
- `POST /api/schedule`
- `PUT /api/schedule/<slot_id>`
- `DELETE /api/schedule/<slot_id>`
- `GET /api/schedule/provider/<provider_id>`

### Availability

- `GET /api/availability/<provider_id>`

### Cancellation Policies

- `POST /api/cancellation-policy`
- `GET /api/cancellation-policy/<service_id>`
- `PUT /api/cancellation-policy/<policy_id>`

## Resetting Local Data

To reset the local SQLite database during development, stop the server and delete:

```bash
rm -rf instance
```

Then run `python app.py` again.
