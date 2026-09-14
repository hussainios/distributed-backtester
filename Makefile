.PHONY: install test lint typecheck check run

install:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy src

check: lint typecheck test

run:
	uvicorn backtester.main:app --reload

