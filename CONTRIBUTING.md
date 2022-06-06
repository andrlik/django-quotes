# How to contribute

Contributions to either the code, localization, or the documentation are very welcome!

## Development task runner

We use [`just`](https://github.com/casey/just) to execute common tasks. It is available for any platform. Once installed, you can see a list of available commands by running `just --list`.

## Dependencies

We use `poetry` to manage the Python [dependencies](https://github.com/python-poetry/poetry).
If you don't have `poetry`, you should install with `just poetry-download`.

To install dependencies and prepare [`pre-commit`](https://pre-commit.com/) hooks you would need to run the `setup` command:

```bash
just setup
```

To activate your `virtualenv` run `poetry shell`.

## Running updates

After pulling new updates from the repository you can quickly install updated dependencies and run database migrations by running `just update`.

## Codestyle

After installation you may execute code formatting.

```bash
just codestyle
```

### Checks

Many checks are configured for this project.

To run your test suite:

```bash
just test
```

To use mypy for type checking run `just mypy`.

Command `just check-codestyle` will check black, isort and darglint.

The `just check-safety` command will look at the security of your code.

To run **ALL** checks, including test suite, codestyle, mypy, and safety:

```bash
just lint
```

### Before submitting

Before submitting your code please do the following steps:

1. Add any changes you want
2. Add tests for the new changes
3. Edit documentation if you have changed something significant
4. Run `just codestyle` to format your changes.
5. Run `just lint` to ensure that types, security and docstrings are okay.
6. Add your name to the `CONTRIBUTERS.txt` file.

## Other help

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.
