SHELL := /bin/bash

.PHONY: venv install test lint docs-lint precommit-install

venv:
	python -m venv .venv

install: venv
	# Activate venv and install dev extras
	. .venv/bin/activate && pip install -e '.[dev]'

test:
	pytest -q

lint: docs-lint
	pytest -q

docs-lint:
	markdownlint "**/*.md" --config .markdownlint.json

precommit-install:
	python -m pip install --upgrade pip
	python -m pip install pre-commit
	pre-commit install
