# RC4LaundryBot2021

Revamped laundry bot for RC4 under CSC IT.

## Running Locally

First create a virtual environment and install dev dependencies.

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

## API

Copy the contents of `api/.env.example` to a new file named `api/.env`. Use `pip install -r api/requirements.txt` to install the dependencies.
From the `api/` directory, run `docker-compose up -d` to spin up two CockroachDB containers. One is used for testing, and another for development.

To start the server, run `uvicorn api.main:app --reload` in the root directory, which also watches for code changes. The default port is 8000.

### Testing

Tests for the API can be run with either `unittest` or `pytest`, and requires the `RUN_ENV` environment variable to be set to "test".

Using `make test` will run all tests with `pytest`.

### Deploying

The API is currently deployed to Google Cloud Platform, with most of the provisioning managed by [Terraform](https://www.terraform.io/). The relational database is a free [CockroachDB cluster](https://www.cockroachlabs.com/).

1. [Create a new project](https://console.cloud.google.com) in Google Cloud. Take note of the assigned project ID and project number.
2. Create a free [CockroachDB cluster](https://cockroachlabs.cloud/); Postgres will also work fine. Note the connection string.
3. Copy the contents of `terraform.tfvars.example` into `terraform.tfvars`, and fill in the variables.
4. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install), which provides the `gcloud` command. Then run `gcloud init` to authenticate.
5. If all went well, run these commands individually from the `api/terraform` directory.

```shell
terraform init
terraform plan
terraform apply
```
