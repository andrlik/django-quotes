# Lists all available commands.
help:
  just --list

# Installs pre-commit into your clone of the git repo.
_pre-commit-install:
  pre-commit install

# Install all dependencies and pypy types
_install:
  rye sync
  rye run mypy --non-interactive src/django_quotes

# Installs pre-commit into git clone, python dependencies, and mypy types.
setup: _pre-commit-install _install

# Resync python environment with requirements and run database migrations.
update: _install
  rye run python manage.py migrate

# Runs the Django development server.
server:
  rye run python manage.py runserver

# Opens a Python shell as provided by shell.
console:
  rye run python manage.py shell

# Opens a database shell for project DB.
db:
  rye run python manage.py dbshell

# Runs pyupgrade, isort, and black against project files.
codestyle:
  rye run pyupgrade --exit-zero-even-if-changed --py39-plus **/*.py
  rye run isort --settings-path pyproject.toml ./
  rye run black --config pyproject.toml ./

# Run test suite.
test:
  rye run pytest -c pyproject.toml

# Runs isort, black, and darglint in check-only mode.
check-codestyle:
  rye run isort --diff --check-only --settings-path pyproject.toml ./
  rye run black --diff --check --config pyproject.toml ./
  rye run darglint --verbosity 2 django_quotes tests

# Runs mypy type checking.
mypy:
  rye run mypy --non-interactive --config-file pyproject.toml src/django_quotes

# Runs bandit checks.
check-safety:
  rye run bandit -ll --recursive src/django_quotes

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
