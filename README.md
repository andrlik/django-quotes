# Django Quotes

A simple reusable [Django](https://www.djangoproject.com) app that allows you to collect quotes from arbitrary groups of characters, and then serve random quotes or Markov-chain generated sentences based upon them. Includes a Bootstrap compatible set of templates an optional REST API.

![PyPI](https://img.shields.io/pypi/v/django-quotes)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/andrlik/django-quotes/blob/main/.pre-commit-config.yaml)
[![License](https://img.shields.io/github/license/andrlik/django-quotes)](https://github.com/andrlik/django-quotes/blob/main/LICENSE)
[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/rye/main/artwork/badge.json)](https://rye-up.com)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/andrlik/django-quotes/releases)
![Test results](https://github.com/andrlik/django-quotes/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/andrlik/django-quotes/badge.svg?branch=main)](https://coveralls.io/github/andrlik/django-quotes?branch=main)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://andrlik.github.io/django-quotes/)

## Features

- Documentation and a full test suite.
- Support for abstract grouping of quote sources.
- Convenience methods for fetching a random quote.
- Object-level permissions via [django-rules](https://github.com/dfunckt/django-rules).
- Generate sentences based off of a Markov-chain for individual sources and groups using natural language processing. (via [django-markov](https://github.com/andrlik/django-markov))
- Bootstrap-compatible templates.
- A simple REST API for fetching data via JSON with CORS support.

Check out [the documentation](https://andrlik.github.io/django-quotes/) for installation and quickstart instructions.
