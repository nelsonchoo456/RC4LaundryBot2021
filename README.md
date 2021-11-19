# RC4LaundryBot2021

Revamped laundry bot for RC4 under CSC IT

## Running Locally

Create a virtual environment with `python -m venv .venv` , then install dependencies with `pip install -r requirements.txt`.

### API

Rename `api/.env.example` to `api/.env`. Navigate to `api/`, then use `docker-compose up -d` to spin up Postgres.
Running `uvicorn main:app` from within `api/` will start the server on port 8000.