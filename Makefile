.PHONY: test fmt seed

test:
	export RUN_ENV="test"
	python -m pytest

fmt:
	python -m black .
	python -m isort .

seed:
	python -m api.db.seed
