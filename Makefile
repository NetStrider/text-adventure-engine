SHELL := /bin/bash

.PHONY: venv install test lint docs-lint precommit-install typecheck coverage

venv:
	python -m venv .venv

install: venv
	# Activate venv and install dev extras
	. .venv/bin/activate && pip install -e '.[dev]'

test:
	pytest -q

lint: docs-lint
	pytest -q

typecheck:
	mypy src

coverage:
	pytest -q --cov=src --cov-report=term-missing --cov-report=xml

docs-lint:
	markdownlint "**/*.md" --config .markdownlint.json

precommit-install:
	python -m pip install --upgrade pip
	python -m pip install pre-commit
	pre-commit install
