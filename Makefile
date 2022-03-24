# Initial Makefile based on https://github.com/TezRomacH/python-package-template
# Originally written by Roman Tezikov and released under an MIT license.

#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Docker variables
IMAGE := django_quotes
VERSION := latest
.DEFAULT_GOAL := help

#* Poetry
## poetry-download     : Downloads and installs poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

## poetry-remove       : Removes poetry
.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

## install             : Locks poetry, installs dependencies and mypy types.
#* Installation
.PHONY: install
install:
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n
	poetry run mypy --install-types --non-interactive django_quotes

## pre-commit-install  : Installs pre-commit into local git repo.
.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Formatters
## codestyle           : Runs pyupgrade, isort, and black against project files.
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py39-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

## formatting          : Alias for codestyle.
.PHONY: formatting
formatting: codestyle

#* Linting
## test                : Runs test suite.
.PHONY: test
test:
	poetry run pytest -c pyproject.toml

## check-codestyle     : Runs isort, black, and darglint in check-only mode.
.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run darglint --verbosity 2 django_quotes tests

## mypy                : Runs mypy type checking.
.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml django_quotes

## check-safety        : Runs poetry safety checks and bandit checks.
.PHONY: check-safety
check-safety:
	poetry check
	poetry run safety check --full-report
	poetry run bandit -ll --recursive django_quotes tests

## lint                : Runs test suite, check-codestyle, mypy, and check-safety
.PHONY: lint
lint: test check-codestyle mypy check-safety

#* Cleaning
## pycache-remove      : Removes pycache directories and files.
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

## build-remove        : Removes generated builds.
.PHONY: build-remove
build-remove:
	rm -rf build/

## clean-all           : Removes pycache directories and files, and generated builds.
.PHONY: clean-all
clean-all: pycache-remove build-remove

## help                : Prints this help message.
.PHONY: help
help: Makefile
	@sed -n 's/^##//p' $<
