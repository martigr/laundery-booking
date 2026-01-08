# Laundry Booking System

A Flask-based web application for managing shared laundry room reservations in apartment buildings.

## Features

- User authentication with login/password
- Apartment-based reservations
- Daily time slots (Vormittag, Nachmittag, Abend)
- Reservation calendar view
- User profile management

## Requirements

- Python 3.13+
- Flask
- SQLite3 (built-in)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

```bash
cd laundery
python app.py
```

The app will be available at `http://localhost:5000`

## Docker

Build and run with Docker:

```bash
docker build -t laundery-booking .
docker run -p 5000:5000 laundery-booking
```

## Database

The app uses SQLite with automatic schema initialization. The database file (`reservations.db`) is created on first run.

## Adding Apartments and Users

Use the `seed.py` script to populate the database with apartments and users:

```bash
cd laundery
python seed.py
```

Edit `seed.py` to customize apartment names and user credentials before running.

## Default Credentials

Update the secret key in `app.py` before deploying to production.
