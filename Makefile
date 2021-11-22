.PHONY test:
	export RUN_ENV="test"; \
	python -m pytest; \

.PHONY fmt:
	python -m black .; \
	python -m isort .; \
