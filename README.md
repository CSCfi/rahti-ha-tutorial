# Rahti HA Tutorial — Flask DB Viewer

A simple Flask application that connects to a PostgreSQL database and exposes its tables through a web UI. It also serves Prometheus metrics for observability.

This app is used as the sample workload in the following CSC tutorials:

- [High Availability on Pouta](https://docs.csc.fi/cloud/pouta/tutorials/high-availability/)
- [High Availability on Rahti](https://docs.csc.fi/cloud/rahti/tutorials/intermediate/high-availability/)

## Features

- Browse all tables and their contents via a web UI
- Prometheus metrics endpoint at `/metrics`
- Structured request logging (method, path, HTTP status, latency)
- Waits for PostgreSQL to be available before starting

## Requirements

- Python 3.11+
- PostgreSQL
- Dependencies listed in `requirements.txt`

## Configuration

The app is configured through environment variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/postgres` | PostgreSQL connection string |
| `PORT` | `5000` | Port the HTTP server listens on |
| `APP_RETRY` | `15` | Number of seconds to wait for the database before giving up |

## Running with Docker

Build and run the container:

```bash
docker build -t rahti-ha-tutorial .
docker run -e DATABASE_URL=postgresql://user:pass@host:5432/dbname -p 5000:5000 rahti-ha-tutorial
```

The container entrypoint uses `wait-for-postgres.sh` to wait for the database before starting the app.

## Running directly

Install dependencies (ideally inside a virtualenv):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the app:

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname python app.py
```

## Running as a systemd service

A service unit file is provided at `rahti-ha-tutorial.service`.

**1. Edit the unit file** to match your deployment:

- `User` / `Group` — the system user that will run the app
- `WorkingDirectory` — where the app is deployed (e.g. `/opt/rahti-ha-tutorial`)
- `DATABASE_URL` — your actual PostgreSQL connection string
- Python path — update `ExecStart` if not using a virtualenv

**2. Install and enable the service:**

```bash
sudo cp rahti-ha-tutorial.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rahti-ha-tutorial
```

**3. Check status and logs:**

```bash
sudo systemctl status rahti-ha-tutorial
journalctl -u rahti-ha-tutorial -f
```

The service uses `wait-for-postgres.sh` via `ExecStartPre` to wait for the database before the app starts, and restarts automatically on failure.

## Endpoints

| Path | Description |
|---|---|
| `/` | Lists all tables in the connected database |
| `/table/<name>` | Shows all rows in the given table |
| `/metrics` | Prometheus metrics |
