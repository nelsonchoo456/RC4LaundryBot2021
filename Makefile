.PHONY: test fmt seed refresh-api-spec

port ?= 8000

test:
	export RUN_ENV="test"
	python -m pytest

fmt:
	python -m black .
	python -m isort .

seed:
	python -m api.db.seed

# Utility script to get yml for the openapi spec
# Requires curl, yq, and the dev server running
refresh-api-spec:
	curl localhost:$(port)/openapi.json | yq -y > api/openapi-spec.yml
