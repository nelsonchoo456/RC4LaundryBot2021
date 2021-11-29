# Using this demo as a reference.
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/HEAD/run/helloworld/Dockerfile
FROM python:3.8

# Set the database uri when building the image
ARG db_uri
ENV DB_URI $db_uri

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

WORKDIR $APP_HOME

# Install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . ./api

# Download CA Certificate for CockroachDB Cloud
RUN curl --create-dirs -o $HOME/.postgresql/root.crt -O https://cockroachlabs.cloud/clusters/fe4dfee9-7787-4080-99b9-47518a1ca6e9/cert

# Seed database with default machines
RUN python -m api.db.seed

# Start server
# The $PORT variable is set by Google Cloud
CMD exec gunicorn api.main:app --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0
