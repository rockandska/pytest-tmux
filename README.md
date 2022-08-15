# pytest-tmux

[![PyPI version](https://img.shields.io/pypi/v/pytest-tmux.svg)](https://pypi.org/project/pytest-tmux)

[![Python versions](https://img.shields.io/pypi/pyversions/pytest-tmux.svg)](https://pypi.org/project/pytest-tmux)

[![See Build Status on AppVeyor](https://ci.appveyor.com/api/projects/status/github/rockandska/pytest-tmux?branch=master)](https://ci.appveyor.com/project/rockandska/pytest-tmux/branch/master)

A pytest plugin that enables tmux driven tests

------------------------------------------------------------------------

## Features

- Enable tmux driven tests
- Enable screen assertion
- Enable row assertion

## Requirements

- python >= 3.7
- python libtmux==0.16
- pytest
- tmux

## Installation

You can install "pytest-tmux" via [pip](https://pypi.org/project/pip/)
from [PyPI](https://pypi.org/project):

    $ pip install pytest-tmux

## Purpose and design

This plugin is intend to help users who whant to test interrative cli.
When using `tmux` fixture it basically :
- create a tmux server (socket create in tmux tmpdir)
- create a session automatically when requested with name based on the name of test file
- create a window automatically when requested with name based on the name of the test

Configuration could be set on different level :
- cli args (see --tmux-* switch with pytest --help)
- at the test level with tmux_cfg marker
- dynamically inside test with `tmux.set()`
- using `tmux.screen() / tmux.row()` (timeout / delay)


## Usage

### Basic example

#### Success

#### Code
```python
import pytest
from inspect import cleandoc

def test_assert(tmux):
    # Set some options before session / windows is started
    tmux.set(window_command='env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile')
    assert tmux.screen() == '$'
    tmux.send_keys(r'printf "  Hello World  .\n\n"')
    expected=r"""
    $ printf "  Hello World  .\n\n"
      Hello World  .

    $
    """
    assert tmux.screen() == cleandoc(expected)
```

### Failure

#### Code
```python
import pytest
from inspect import cleandoc

def test_assert(tmux):
    # Set some options before session / windows is started
    tmux.set(window_command='env -i PS1="# " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile')
    assert tmux.row(0) == '$'
```

#### Output

```
>       assert tmux.row(0) == '$'
E       assert failed
E         > Common line
E         - Left
E         + Right
E         -------------
E         - #
E         + $
E         -------------
```

### Waiting for a long process

```python
import pytest
from inspect import cleandoc

def test_assert(tmux):
    # Set some options before session / windows is started
    tmux.set(window_command='env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile')
    assert tmux.row(0) == '$'
    tmux.send_keys('sleep 5')
    assert tmux.row(0) == '$ sleep 5'
    expected = """
    $ sleep 5
    $
    """
    assert tmux.screen(timeout=6, delay=0.5) == cleandoc(expected)
```

### Debug

If needed, a debug mode is available with `--tmux-debug`.
It will prompt you to :
- open the tmux session for the current test
- press enter to continue on :
    - send_keys
    - kill_session

## Contributing

Contributions are very welcome.

### Dev requirements

- minor python3 versions present in .python-version
- pyenv > v2.3.9 ( optional but recommended )
- virtualenv (will be installed by `make venv` if not available)

### Start hacking

#### Install python versions used for tests ( recommended )

```shell
pyenv install
```

/!\ Install multiple versions in a single command only available in pyenv > 2.3.9

#### Create the project virtualenv

```shell
$ make venv
```

This target does the following:

- installs `virtualenv` if not found
- creates a venv in `.venv` for `dev-requirements.txt`
- installs `dev-requirements.txt`
- creates a `.python-venv` symlink to `.venv/bin/activate`

### Run tests

Tests are driven by tox / make

#### Run with make

Example:
```shell
$ make test
```

#### Run with tox or free commands

Example:
```shell
$ source .python-venv
$ tox
$ poetry run pytest tests/
```

#### Formater

`black` and `isort` run in check mode by default

check mode could be removed by running the env as :
```shell
$ source .python-venv
$ tox -e black --
$ tox -e isort --
```

### Update tox.ini / pyproject.toml

- Update `tox.ini.j2` to update `tox.ini`
- Update `pyproject.ini.j2` to update `pyproject.ini`
- Update `.python-version` to add a new python version (order is important)

## License

Distributed under the terms of the
[MIT](http://opensource.org/licenses/MIT) license, "pytest-tmux" is free
and open source software

## Issues

If you encounter any problems, please [file an
issue](https://github.com/rockandska/pytest-tmux/issues) along with a
detailed description.
