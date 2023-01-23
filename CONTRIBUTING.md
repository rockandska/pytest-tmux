Contributions are very welcome.

## Dev requirements

- minor python3 versions present in .python-version
- pyenv > v2.3.9 ( optional but recommended )
- virtualenv (will be installed by `make venv` if not available)

## Start hacking

### Install python versions used for tests ( recommended )

```shell
pyenv install
```

/!\ Install multiple versions in a single command only available in pyenv > 2.3.9

### Create the project virtualenv

```shell
$ make venv
```

This target does the following:

- installs `virtualenv` if not found
- creates a venv in `.venv` for `dev-requirements.txt`
- installs `dev-requirements.txt`
- creates a `.python-venv` symlink to `.venv/bin/activate`

## Run tests

Tests are driven by tox / make

### Run with make

Example:
```shell
$ make test
```

### Run with tox or free commands

Example:
```shell
$ source .python-venv
$ tox
$ poetry run pytest tests/
```

### Formater

`black` and `isort` run in check mode by default

check mode could be removed by running the env as :
```shell
$ source .python-venv
$ tox -e black --
$ tox -e isort --
```

## Update tox.ini / pyproject.toml

- Update `tox.ini.j2` to update `tox.ini`
- Update `pyproject.ini.j2` to update `pyproject.ini`
- Update `.python-version` to add a new python version (order is important)

