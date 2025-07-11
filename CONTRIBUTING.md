# How to contribute

Contributions to either the code, localization, or the documentation are very welcome!

## Development task runner

We use [`just`](https://github.com/casey/just) to execute common tasks. It is available for any platform. Once installed, you can see a list of available commands by running `just`.

<!-- [[[cog
import subprocess
import cog

list = subprocess.run(["just"], stdout=subprocess.PIPE)
cog.out(
    f"```\n{list.stdout.decode('utf-8')}```"
)
]]] -->
```
Available recipes:
    help                         # Lists all available commands.

    [lifecycle]
    bootstrap                    # Setup the project and update dependencies.
    build *ARGS                  # Build Python package
    clean                        # Removes pycache directories and files, and generated builds.
    docs *ARGS                   # Access mkdocs commands
    fresh                        # Destroy and recreate the virtual environments from scratch
    upgrade                      # Update project dependencies

    [qa]
    check-types                  # Check types
    fmt                          # Run just formatter and ruff formatter.
    lint                         # Run ruff linting
    safety                       # Runs bandit safety checks.
    test *ARGS                   # Run the test suite
    tox *ARGS                    # Run tox for code style, type checking, and multi-python tests. Uses run-parallel.

    [run]
    browser                      # Open a web browser to the development server.
    manage *ARGS                 # Access Django management commands.
    req path="app/groups/" *ARGS # Send a request to the development server to print to stdout. Uses curl if present, else httpie.
    serve *ARGS                  # Run the development server

    [uv]
    uv-install                   # Downloads and installs uv on your system.
    uv-uninstall                 # Uninstall uv
    uv-update                    # Update uv
```
<!-- [[[end]]] -->

## Dependencies

We use `uv` to manage the Python [dependencies](https://rye-up.com).
If you don't have `uv`, you should install with `just uv-install`.

To install dependencies and prepare [`pre-commit`](https://pre-commit.com/) hooks you would need to run the `bootstrap` command:

```bash
just bootstrap
```

## Running updates

After pulling new updates from the repository you can quickly install updated dependencies and run database migrations by running `just bootstrap`.

## Codestyle

After installation you may execute code formatting.

```bash
just fmt
```

### Checks

Many checks are configured for this project.

To run your test suite:

```bash
just test
```

To use pyright for type checking run:
```bash
just check-types
```

To run linting:

```bash
just check
```

The `just safety` command will look at the security of your code.

### Before submitting

Before submitting your code please do the following steps:

1. Add any changes you want
2. Add tests for the new changes
3. Edit documentation if you have changed something significant
4. Run `just fmt` to format your changes.
5. Run `just check` to ensure that types, security and docstrings are okay.
6. Add your name to the `CONTRIBUTERS.txt` file.

## Other help

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.
