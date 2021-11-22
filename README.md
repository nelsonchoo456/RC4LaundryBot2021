# RC4LaundryBot2021

Revamped laundry bot for RC4 under CSC IT

## Running Locally

First create a virtual environment and install dev dependencies.

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

### API

Rename `api/.env.example` to `api/.env`. Use `pip install -r api/requirements.txt` to install the dependencies for api.
From the `api/` directory, run `docker-compose up -d` to spin up two Postgres containers. One is used for testing, and another for development.

To start the server, run `uvicorn api.main:app` in the root directory. The default port is 8000.

#### Testing

Tests can be run with either `unittest` or `pytest`, and requires the `$RUN_ENV` environment variable to be set to "test".
Using `make test` will run all test with `pytest`.
