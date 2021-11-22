.PHONY: test
test:
	export RUN_ENV="test"; \
	python -m pytest; \

.PHONY: fmt
fmt:
	python -m black .; \
	python -m isort .; \

.PHONY: seed
seed:
	python -m api.db.seed
