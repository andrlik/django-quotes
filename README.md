# Django Quotes

A simple reusable [Django](https://www.djangoproject.com) app that allows you to collect quotes from arbitrary groups of characters, and then serve random quotes or Markov-chain generated sentences based upon them. Includes a Bootstrap compatible set of templates an optional REST API.

[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/andrlik/django-quotes/blob/main/.pre-commit-config.yaml)
[![License](https://img.shields.io/github/license/andrlik/django-quotes)](https://github.com/andrlik/django-quotes/blob/main/LICENSE)
![Test results](https://github.com/andrlik/django-quotes/actions/workflows/ci.yml/badge.svg)
![Codestyle check results](https://github.com/andrlik/django-quotes/actions/workflows/codestyle.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/andrlik/django-quotes/badge.svg?branch=main)](https://coveralls.io/github/andrlik/django-quotes?branch=main)
[![Documentation Status](https://readthedocs.org/projects/django-quotes-app/badge/?version=latest)](https://django-quotes-app.readthedocs.io/en/latest/?badge=latest)

## Features

- Documentation and a full test suite.
- Support for abstract grouping of quote sources.
- Convenience methods for fetching a random quote.
- Object-level permissions via [django-rules](https://github.com/dfunckt/django-rules).
- Generate sentences based off of a Markov-chain for individual sources and groups using natural language processing.
- Bootstrap-compatible templates.
- A simple REST API for fetching data via JSON with CORS support.

Check out [the documentation](https://django-quotes-app.readthedocs.io/en/latest/) for installation and quickstart instructions.
