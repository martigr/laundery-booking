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

## Running Locally (Development)

Use the built-in Flask server only for development. From the `laundery` folder:

```bash
# set FLASK_APP if needed and run for development
cd laundery
python app.py
```

The app will be available at `http://localhost:5000`.

## Running Locally (Production-like)

Run a production WSGI server on your machine. Example (Unix):

```bash
# using Gunicorn
pip install -r requirements.txt
cd laundery
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

This guide targets Linux-based deployments; on Linux use Gunicorn as shown above. For Windows, use Docker or WSL if needed.

## Docker (Production)

Set a safe secret and run Gunicorn inside the container:

```bash
# build
docker build -t laundery-booking .
# run (replace SECRET_KEY and optionally DATABASE)
docker run -e SECRET_KEY='a-very-long-random-secret' -p 5000:5000 laundery-booking
```

Notes:
- Set `SECRET_KEY` to a long random string in production. Do not commit it to source control.
- You can set `DATABASE` to point to a persistent file or external DB.
- The app exposes `/health` for health checks.

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
