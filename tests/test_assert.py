# -*- coding: utf-8 -*-


def test_assert_screen(pytester):

    src = r'''
        import pytest
        from inspect import cleandoc

        def test_assert(tmux):
            tmux.config.session.window_command = 'env -i PS1="$ " TERM="xterm-256color" /usr/bin/env bash --norc --noprofile'
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


def test_wait_sleep(pytester):
    src = r'''
        import pytest
        from inspect import cleandoc

        def test_wait_sleep(tmux):
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
    '''

    pytester.makepyfile(src)
    result = pytester.runpytest("-vv", "-s")

    assert result.ret == 0
