all: error

error:
	@echo "Please choose one of the following target: install, tests"

tests:
	@poetry run python -m pytest -v tests

install:
	@pip install poetry
	@poetry install

.PHONY: tests install
