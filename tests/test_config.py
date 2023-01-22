# -*- coding: utf-8 -*-
from inspect import cleandoc


def test_default_cfg(pytester, tmp_path_factory):
    """test default config values"""
    src = cleandoc(
        """
        def test_default_config(tmux):
            assert tmux.config.server.socket_path == '{}'
            assert 'config_file' not in tmux.config.server
            assert 'colors' not in tmux.config.server
            assert tmux.session.name == 'test_default_cfg_test_default_config'
            assert tmux.window.name == 'test_default_config'
            assert tmux.config.assertion.timeout == 2
            assert tmux.config.assertion.delay == 0.5
    """
    ).format(
        "{}/basetemp/tmux.socket".format(str(tmp_path_factory.getbasetemp())),
    )
    pytester.makepyfile(src)
    result = pytester.runpytest("-s")
    assert result.ret == 0


def test_cmd_cfg(pytester):
    """test config through command line arguments"""
    cmd_options = [
        "--tmux-debug",
        "--tmux-socket-path",
        "{}/tmux.socket".format(pytester.path),
        "--tmux-config-file",
        "{}/tmux.cfg".format(pytester.path),
        "--tmux-colors",
        "256",
        "--tmux-start-directory",
        "{}".format(pytester.path),
        "--tmux-window-command",
        "/bin/sh",
        "--tmux-window-width",
        "32",
        "--tmux-window-height",
        "32",
        "--tmux-assertion-timeout",
        "5",
        "--tmux-assertion-delay",
        "1",
    ]
    src = cleandoc(
        """
        def test_cmd_config(tmux):
            assert tmux.config.plugin.debug == True
            assert tmux.config.server.socket_path == '{}'
            assert tmux.config.server.config_file == '{}'
            assert tmux.config.server.colors == 256
            assert tmux.config.session.start_directory == '{}'
            assert tmux.config.session.window_command == '/bin/sh'
            assert tmux.config.session.x == 32
            assert tmux.config.session.y == 32
            assert tmux.config.assertion.timeout == 5
            assert tmux.config.assertion.delay == 1
    """
    ).format(
        "{}/tmux.socket".format(pytester.path),
        "{}/tmux.cfg".format(pytester.path),
        "{}".format(pytester.path),
    )

    pytester.makepyfile(src)
    result = pytester.runpytest("-s", *cmd_options)
    assert result.ret == 0


def test_env_cfg(pytester, monkeypatch):
    """test config through env variables"""
    monkeypatch.setenv("PYTEST_TMUX_DEBUG", "1")
    monkeypatch.setenv(
        "PYTEST_TMUX_SOCKET_PATH", "{}/tmux.socket_env".format(pytester.path)
    )
    monkeypatch.setenv(
        "PYTEST_TMUX_CONFIG_FILE", "{}/tmux.cfg_env".format(pytester.path)
    )
    monkeypatch.setenv("PYTEST_TMUX_COLORS", "8")
    monkeypatch.setenv("PYTEST_TMUX_START_DIRECTORY", "/tmp")
    monkeypatch.setenv("PYTEST_TMUX_WINDOW_COMMAND", "sh")
    monkeypatch.setenv("PYTEST_TMUX_WINDOW_WIDTH", "34")
    monkeypatch.setenv("PYTEST_TMUX_WINDOW_HEIGHT", "34")
    monkeypatch.setenv("PYTEST_TMUX_ASSERTION_TIMEOUT", "12")
    monkeypatch.setenv("PYTEST_TMUX_ASSERTION_DELAY", "3")
    src = cleandoc(
        """
        import os
        def test_env_config(tmux):
            assert tmux.config.plugin.debug == True
            assert tmux.config.server.socket_path == "{}"
            assert tmux.config.server.config_file == "{}"
            assert tmux.config.server.colors == 8
            assert tmux.config.session.start_directory == '/tmp'
            assert tmux.config.session.window_command == 'sh'
            assert tmux.config.session.x == 34
            assert tmux.config.session.y == 34
            assert tmux.config.assertion.timeout == 12
            assert tmux.config.assertion.delay == 3
    """
    ).format(
        "{}/tmux.socket_env".format(pytester.path),
        "{}/tmux.cfg_env".format(pytester.path),
    )

    pytester.makepyfile(src)
    result = pytester.runpytest("-s")

    assert result.ret == 0


def test_live_cfg(pytester):
    src = cleandoc(
        """
        def test_live_config(tmux):
            tmux.config.plugin.debug = True
            tmux.config.server.socket_path = '{}'
            tmux.config.server.config_file = '{}'
            tmux.config.server.colors = 256
            tmux.config.session.start_directory = '{}'
            tmux.config.session.window_command = '/bin/sh'
            tmux.config.session.x = 32
            tmux.config.session.y = 32
            tmux.config.assertion.timeout = 5
            tmux.config.assertion.delay = 1
            assert tmux.config.plugin.debug == True
            assert tmux.config.server.socket_path == '{}'
            assert tmux.config.server.config_file == '{}'
            assert tmux.config.server.colors == 256
            assert tmux.config.session.start_directory == '{}'
            assert tmux.config.session.window_command == '/bin/sh'
            assert tmux.config.session.x == 32
            assert tmux.config.session.y == 32
            assert tmux.config.assertion.timeout == 5
            assert tmux.config.assertion.delay == 1
    """
    ).format(
        "{}/tmux.socket".format(pytester.path),
        "{}/tmux.cfg".format(pytester.path),
        "{}".format(pytester.path),
        "{}/tmux.socket".format(pytester.path),
        "{}/tmux.cfg".format(pytester.path),
        "{}".format(pytester.path),
    )

    pytester.makepyfile(src)
    result = pytester.runpytest("-s")
    assert result.ret == 0


def test_fixture_cfg(pytester):
    src = cleandoc(
        """
        import pytest
        @pytest.fixture(scope='session')
        def tmux_server_config():
            return {{
                'socket_path': '{}',
                'config_file': '{}',
                'colors': 256,
            }}

        @pytest.fixture()
        def tmux_session_config():
            return {{
                'start_directory': '{}',
                'window_command': '/bin/sh',
                'x': 32,
                'y': 32,
            }}

        @pytest.fixture()
        def tmux_assertion_config():
            return {{
                'timeout': 5,
                'delay': 1
            }}

        def test_fixture_config(tmux):
            assert tmux.config.server.socket_path == '{}'
            assert tmux.config.server.config_file == '{}'
            assert tmux.config.server.colors == 256
            assert tmux.config.session.start_directory == '{}'
            assert tmux.config.session.window_command == '/bin/sh'
            assert tmux.config.session.x == 32
            assert tmux.config.session.y == 32
            assert tmux.config.assertion.timeout == 5
            assert tmux.config.assertion.delay == 1
    """
    ).format(
        "{}/tmux.socket".format(pytester.path),
        "{}/tmux.cfg".format(pytester.path),
        "{}".format(pytester.path),
        "{}/tmux.socket".format(pytester.path),
        "{}/tmux.cfg".format(pytester.path),
        "{}".format(pytester.path),
    )

    pytester.makepyfile(src)
    result = pytester.runpytest("-s")
    assert result.ret == 0


def test_marker_cfg(pytester):
    """test config through markers"""
    src = cleandoc(
        """
        import pytest
        @pytest.mark.tmux_session_cfg(
            start_directory='/test',
            window_command='bash',
            x=31,
            y=33,
        )
        @pytest.mark.tmux_assertion_cfg(
            timeout=3,
            delay=3
        )
        def test_marker_config(tmux):
            assert tmux.config.session.start_directory == '/test'
            assert tmux.config.session.window_command == 'bash'
            assert tmux.config.session.x == 31
            assert tmux.config.session.y == 33
            assert tmux.config.assertion.timeout == 3
            assert tmux.config.assertion.delay == 3
    """
    )
    pytester.makepyfile(src)
    result = pytester.runpytest("-s")
    assert result.ret == 0
