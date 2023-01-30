# Examples

## Basic example

### Success

#### Code

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

### Failure

#### Code

```python
import pytest
from inspect import cleandoc

def test_assert(tmux):
    # Set some options before session / windows is started
    tmux.config.session.window_command='env -i PS1="# " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile'
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

## Waiting for a long process

```python
import pytest
from inspect import cleandoc

def test_assert(tmux):
    # Set some options before session / windows is started
    tmux.config.session.window_command='env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile'
    assert tmux.row(0) == '$'
    tmux.send_keys('sleep 5')
    assert tmux.row(0) == '$ sleep 5'
    expected = """
    $ sleep 5
    $
    """
    assert tmux.screen(timeout=6, delay=0.5) == cleandoc(expected)
```

