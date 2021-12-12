# RC4LaundryBot2021

Revamped laundry bot for RC4 under CSC IT.

## JSON API

### Requirements

Development for the JSON API requires these.

- Python 3.8
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Serverless CLI](https://www.serverless.com/framework/docs/getting-started)
- NPM

### Development

1. Create a virtual environment and install dependencies.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements.dev.txt
npm install
```

2. Copy the contents of `.env.example` to a new file named `.env.local`. The `.env.example` file contains default secrets/settings for local development.
3. Start the dev server with the commands below. The default port is 8000, and OpenAPI docs are at http://localhost:8000/docs.

```bash
sls dynamodb start # <-- in a separate terminal
docker-compose up -d
uvicorn app.main:app --reload
```

### Testing

Tests can be run with pytest.

```
python -m pytest -v
```

### Deployment

This flowchart briefly describes the components of the API.

[![](https://mermaid.ink/img/eyJjb2RlIjoiZmxvd2NoYXJ0IFREXG4gICAgQShSYXNwaSkgLS1QT1NUL1BVVC9QQVRDSC0tPiBCe0FQSX1cbiAgICBCIC0tTWFjaGluZSAmIFJhc3BpIHN0YXRlLS0-IENbKFJlZGlzKV1cbiAgICBCIC0tVXNhZ2UgZGV0YWlsIHJlY29yZHMtLT4gRFsoRHluYW1vREIpXSAgIiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjp0cnVlLCJhdXRvU3luYyI6dHJ1ZSwidXBkYXRlRGlhZ3JhbSI6ZmFsc2V9)](https://mermaid.live/edit#eyJjb2RlIjoiZmxvd2NoYXJ0IFREXG4gICAgQShSYXNwaSkgLS1QT1NUL1BVVC9QQVRDSC0tPiBCe0FQSX1cbiAgICBCIC0tTWFjaGluZSAmIFJhc3BpIHN0YXRlLS0-IENbKFJlZGlzKV1cbiAgICBCIC0tVXNhZ2UgZGV0YWlsIHJlY29yZHMtLT4gRFsoRHluYW1vREIpXSAgIiwibWVybWFpZCI6IntcbiAgXCJ0aGVtZVwiOiBcImRlZmF1bHRcIlxufSIsInVwZGF0ZUVkaXRvciI6dHJ1ZSwiYXV0b1N5bmMiOnRydWUsInVwZGF0ZURpYWdyYW0iOmZhbHNlfQ)

Here are the steps for deploying.

1. First we'll configure a Redis instance. [Redis Labs](https://redis.com/) has a free tier option. Enable the RedisJSON and RediSearch modules when creating the database.
   - Take note of the host, port, and default user password.
2. Set up a `.env` file. This file is used for deployment only and is different from `.env.local`. An example showing the required fields is below.
   - Choose an API key you like.
   - Get the other fields from the Redis Labs console.
   - Once the file is ready, run `make seed-redis` to create the machines in Redis.

```bash
API_KEY=super-secure-key
REDIS_HOST=
REDIS_PORT=
REDIS_DB=0
REDIS_PASS=
```

3. Finally, run `make deploy` to provision the rest of the infrastructure.
   - Run `make deploy` again to push any changes to AWS.

## Miscellaneous

Pre-commit is configure for this repo. If you'd like to use it, follow these steps.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.dev.txt
pre-commit install
pre-commit autoupdate
```
