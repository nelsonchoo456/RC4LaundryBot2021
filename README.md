# RC4LaundryBot2021

Revamped laundry bot for RC4 under CSC IT

## Running Locally

First create a virtual environment and install dependencies.

```shell
python -m venv .venv
pip install -r requirements.txt requirements_dev.txt
```

### API

Rename `api/.env.example` to `api/.env`. 
From the `api/` directory, run `docker-compose up -d` to spin up two Postgres containers. One is used for testing, and another for development.

To start the server, run `uvicorn api.main:app` in the root directory. The default port is 8000.
To verify that everything works, running `./pants test api::` will run all tests for the `api` package.