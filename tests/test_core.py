# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def test_send_keys(pytester: pytest.Pytester) -> None:
    src = r'''
        import pytest
        from inspect import cleandoc

        def test_send_keys(tmux):
            tmux.config.session.window_command = 'env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile'
            assert tmux.screen() == '$'
            tmux.send_keys('ls', enter=False)
            expected=r"""
            $ ls
            """
            assert tmux.screen() == cleandoc(expected)
    '''

    pytester.makepyfile(src)
    result = pytester.runpytest("-vv", "-s")

    assert result.ret == 0
