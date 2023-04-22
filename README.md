# pytest-tmux

[![PyPI version](https://img.shields.io/pypi/v/pytest-tmux.svg)](https://pypi.org/project/pytest-tmux)

[![Python versions](https://img.shields.io/pypi/pyversions/pytest-tmux.svg)](https://pypi.org/project/pytest-tmux)

A pytest plugin that enables tmux driven tests

This plugin is intend to help users who want to test interrative cli.

When using `tmux` fixture it basically :

- creates a tmux server (socket created in pytest tmpdir)
- creates a session automatically
- attach to the window automatically
- attach to the pane automatically

## Warnings

**Until a stable release, it is greatly encouraged to specify a strict version if
you use this tool in your CI since it is in its early development and could be
greatly changed between version.**

## Docs

[https://pytest-tmux.readthedocs.io/](https://pytest-tmux.readthedocs.io)

## Features

- Enable tmux driven tests
- Enable screen assertion with retry
- Enable row assertion with retry
- Allow to debug tests interactively

## Requirements

- python >= 3.7
- pytest
- tmux

## Installation

You can install "pytest-tmux" via [pip](https://pypi.org/project/pip/)
from [PyPI](https://pypi.org/project):

    $ pip install pytest-tmux

## Configuration capabilities

Configuration could be set on different level (in order of precedence):

- Server
    - by overriding tmux_server_config (scope='session') fixture
    - env var
    - cli args (see --tmux-* switch with pytest --help)
- Session
    - by overriding tmux_session_config fixture
    - at the test level with tmux_session_cfg marker
    - dynamically inside test with `tmux.config.session`
    - env var
    - cli args (see --tmux-* switch with pytest --help)
- Assertion
    - by overriding tmux_assertion_config fixture
    - at the test level with tmux_assertion_cfg marker
    - dynamically inside test with `tmux.config.session`
    - when calling `tmux.screen() / tmux.row()` with `timeout` / `delay` argument
    - env var
    - cli args (see --tmux-* switch with pytest --help)


## Usage

### Basic example

```python
import pytest
from inspect import cleandoc

def test_assert(tmux):
    # Set some options before session / windows is started
    tmux.config.session.window_command='env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile'
    assert tmux.screen() == '$'
    tmux.send_keys(r'printf "  Hello World  .\n\n"')
    expected=r"""
    $ printf "  Hello World  .\n\n"
      Hello World  .

    $
    """
    assert tmux.screen() == cleandoc(expected)
```

## License

Distributed under the terms of the
[MIT](http://opensource.org/licenses/MIT) license, "pytest-tmux" is free
and open source software

## Issues

If you encounter any problems, please [file an
issue](https://github.com/rockandska/pytest-tmux/issues) along with a
detailed description.
