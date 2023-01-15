# -*- coding: utf-8 -*-


def test_assert_screen(pytester):

    src = r'''
        import pytest
        from inspect import cleandoc

        def test_assert(tmux):
            tmux.set(window_command='env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile')
            assert tmux.screen() == '$'
            tmux.send_keys(r'printf "  Hello World  .\n\n"')
            expected=r"""
            $ printf "  Hello World  .\n\n"
              Hello World  .

            $
            """
            assert tmux.screen() == cleandoc(expected)
    '''

    pytester.makepyfile(src)
    result = pytester.runpytest("-vv", "-s")

    assert result.ret == 0
