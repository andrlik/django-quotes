# Lists all available commands.
help:
  just --list

# Downloads and installs poetry on your system.
poetry-download:
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

# Uninstalls poetry from your system.
poetry-remove:
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

# Installs pre-commit into your clone of the git repo.
_pre-commit-install:
  poetry run pre-commit install

# Install all dependencies and pypy types
_install:
  poetry install
  poetry run python -m spacy download en_core_web_sm
  poetry run mypy --install-types --non-interactive django_quotes

# Installs pre-commit into git clone, python dependencies, and mypy types.
setup: _pre-commit-install _install

# Resync python environment with requirements and run database migrations.
update: _install
  poetry run python manage.py migrate

# Runs the Django development server.
server:
  poetry run python manage.py runserver

# Opens a Python shell as provided by shell.
console:
  poetry run python manage.py shell

# Opens a database shell for project DB.
db:
  poetry run python manage.py dbshell

# Runs pyupgrade, isort, and black against project files.
codestyle:
  poetry run pyupgrade --exit-zero-even-if-changed --py39-plus **/*.py
  poetry run isort --settings-path pyproject.toml ./
  poetry run black --config pyproject.toml ./

# Run test suite.
test:
  poetry run pytest -c pyproject.toml

# Runs isort, black, and darglint in check-only mode.
check-codestyle:
  poetry run isort --diff --check-only --settings-path pyproject.toml ./
  poetry run black --diff --check --config pyproject.toml ./
  poetry run darglint --verbosity 2 django_quotes tests

# Runs mypy type checking.
mypy:
  poetry run mypy --config-file pyproject.toml django_quotes

# Runs poetry safety and bandit checks.
check-safety:
  poetry check
  poetry run safety check --full-report
  poetry run bandit -ll --recursive django_quotes tests

# Runs test suite, check-codestyle, mypy, and check-safety.
lint: test check-codestyle mypy check-safety

# Removes pycache directories and files.
_pycache-remove:
  find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

# Remove generated builds.
_build-remove:
  rm -rf dist/*

# Removes pycache directories and files, and generated builds.
clean: _pycache-remove _build-remove
