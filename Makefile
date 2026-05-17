#!make
.DEFAULT_GOAL := docker-test

mypy = uv run mypy ./app tests/
pyright = uv run pyright
pytest = uv run pytest
ruff = uv run ruff


.PHONY: install
install:
	uv sync


.PHONY: format
format:
	$(ruff) format .
	$(ruff) check --fix --preview .


.PHONY: docker-lint
docker-lint:
	docker run --rm -i -v $(shell pwd)/.hadolint.yaml:/.config/hadolint.yaml hadolint/hadolint < Dockerfile


.PHONY: python-lint
python-lint:
	$(ruff) format --check .
	$(ruff) check . --preview
	$(mypy)
	$(pyright)


.PHONY: lint
lint: docker-lint python-lint


.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .cache .pytest_cache .mypy_cache .ruff_cache htmlcov
	rm -f .coverage .coverage.*


.PHONY: docker-test
docker-test:
	docker compose -f docker-compose.test.yaml up --build --exit-code-from tests


.PHONY: test-local
test-local:
	$(pytest) --no-header --no-cov -vv tests




.PHONY: migrate
migrate:
	uv run alembic upgrade head


.PHONY: revision
revision:
	uv run alembic revision --autogenerate -m "$(m)"
