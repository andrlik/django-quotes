set dotenv-load := true
set unstable := true

PORT := env("PORT", "8000")
ARGS_TEST := env("_UV_RUN_ARGS_TEST", "")
ARGS_SERVE := env("_UV_RUN_ARGS_SERVE", "")

# Lists all available commands.
@help:
    just --list

@_cog:
    uvx --from cogapp cog -r CONTRIBUTING.md

# ---------------------------------------------- #
# Script to rule them all recipes.               #
# ---------------------------------------------- #

# Install pre-commit hooks
_install-pre-commit: _check-pre-commit
    #!/usr/bin/env bash
    if [[ ! -f .git/hooks/pre-commit ]]; then
      echo "Pre-commit hooks are not installed yet! Doing so now."
      pre-commit install
    fi
    exit 0

# Downloads and installs uv on your system.
[group('uv')]
[linux]
[macos]
[script('bash')]
[unix]
uv-install:
    set -euo pipefail
    if ! command -v uv &> /dev/null;
    then
      echo "uv is not found on path! Starting install..."
      curl -LsSf https://astral.sh/uv/install.sh | sh
    else
      uv self update
    fi

# Downloads and installs uv on your system
[group('uv')]
[script]
[windows]
uv-install:
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Update uv
[group('uv')]
uv-update:
    uv self update

# Uninstall uv
[group('uv')]
uv-uninstall:
    uv self uninstall

[script]
_check-pre-commit:
    if ! command -v pre-commit &> /dev/null; then
      echo "Pre-commit is not installed!"
      exit 1
    fi

[script]
_check-env:
    if [[ -z "$DJANGO_DEBUG" ]]; then
      echo "DJANGO_DEBUG is not set and application will run in production mode." >&2
    fi

# Setup the project and update dependencies.
[group('lifecycle')]
bootstrap: uv-install _install-pre-commit _check-env
    @uv sync --inexact
    @uv pip install pip
    @uv run -m spacy info en_core_web_sm && echo "Lang model is already installed" || uv run -m spacy download en_core_web_sm
    @just manage migrate

# Checks that project is ready for development.
[script]
_check: _check-env _check-pre-commit
    if ! command -v uv &> /dev/null; then
      echo "UV is not installed!"
      exit 1
    fi
    if [[ ! -f ".venv/bin/python" ]]; then
      echo "Virtualenv is not installed! Run 'just bootstrap' to complete setup."
      exit 1
    fi

# Check types
[group('qa')]
check-types: _check
    uv run pyright

# Run just formatter and ruff formatter.
[group('qa')]
fmt: _check
    just --fmt --unstable
    uv run -m ruff format

# Run ruff linting
[group('qa')]
lint: _check
    uv run ruff check src

# Run the test suite
[group('qa')]
test *ARGS: _check
    uv run {{ARGS_TEST}} -m pytest {{ ARGS }}

# Run tox for code style, type checking, and multi-python tests. Uses run-parallel.
[group('qa')]
tox *ARGS: _check
    uvx --python 3.12 --with tox-uv {{ARGS_TEST}} tox {{ ARGS }}

# Runs bandit safety checks.
[group('qa')]
safety: _check
    uv run -m bandit -c pyproject.toml -r src

# Access Django management commands.
[group('run')]
[script('bash')]
manage *ARGS: _check
    DJANGO_SETTINGS_MODULE="tests.django_settings" PYTHONPATH="$PYTHONPATH:$(pwd)" uv run django-admin {{ ARGS }}

# Run the development server
[group('run')]
[script('bash')]
serve *ARGS: _check
    DJANGO_SETTINGS_MODULE="tests.django_settings" PYTHONPATH="$PYTHONPATH:$(pwd)" uv run {{ ARGS_SERVE }} django-admin runserver 127.0.0.1:{{ PORT }} {{ ARGS }}

# Open a web browser to the development server.
[group('run')]
@browser: _check
    uv run -m webbrowser -t http://127.0.0.1:{{ PORT }}

# Send a request to the development server to print to stdout. Uses curl if present, else httpie.
[group('run')]
[script]
req path="app/groups/" *ARGS:
    if ! [ -x "$(command -v curl)" ]; then
        @just _http {{ ARGS }} http://127.0.0.1:{{ PORT }}/{{ path }}
    else
        curl {{ ARGS }} -L http://127.0.0.1:{{ PORT }}/{{ path }}
    fi

# Invoke http from httpie
_http *ARGS:
    uvx --from httpie http {{ ARGS }}

# Access mkdocs commands
[group('lifecycle')]
@docs *ARGS: _check
    uv run mike {{ ARGS }}

# Build Python package
[group('lifecycle')]
@build *ARGS: _check
    uv build {{ ARGS }}

# Removes pycache directories and files.
_pycache-remove:
    find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

# Remove generated builds.
_build-remove:
    rm -rf dist/*

# Remove generated docs
_docs-clean:
    rm -rf site/*

# Remove any generated virtualenvs.
_env-clean:
    rm -rf .venv .tox

# Removes pycache directories and files, and generated builds.
[group('lifecycle')]
clean: _pycache-remove _build-remove _docs-clean

# Destroy and recreate the virtual environments from scratch
[group('lifecycle')]
fresh: _env-clean && bootstrap
    @echo "Previous envs destroyed. Now recreating!"

# Update project dependencies
[group('lifecycle')]
@upgrade: _check
    uv sync --upgrade
