# RC4LaundryBot2021

Revamped laundry bot for RC4 under CSC IT

## Running Locally

Create a virtual environment with `python -m venv .venv` , then install dependencies with `pip install -r requirements.txt requirements_dev.txt`.

### API

Rename `api/.env.example` to `api/.env`. From the `api/` directory, run `docker-compose up -d` to spin up Postgres.
Running `uvicorn api.main:app` in the root directory will start the server on port 8000.