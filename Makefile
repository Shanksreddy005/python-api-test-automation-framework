.PHONY: install test coverage lint format clean

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

test:
	pytest

coverage:
	pytest --cov=tests --cov-report=xml --cov-report=html

lint:
	flake8 tests utils
	ruff check tests utils

format:
	black tests utils
	isort tests utils

clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf reports/*
	rm -rf logs/*
	find . -type d -name __pycache__ -exec rm -r {} +
