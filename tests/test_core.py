# -*- coding: utf-8 -*-
def test_send_keys(testdir, options):
    src = r'''
        import pytest
        from inspect import cleandoc

        def test_send_keys(tmux):
            tmux.set(window_command='env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile')
            assert tmux.screen() == '$'
            tmux.send_keys('ls', enter=False)
            expected=r"""
            $ ls
            """
            assert tmux.screen() == cleandoc(expected)
    '''

    testdir.makepyfile(src)
    result = testdir.runpytest("-vv", "-s")

    assert result.ret == 0
