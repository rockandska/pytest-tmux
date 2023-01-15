# -*- coding: utf-8 -*-
from inspect import cleandoc

def test_default_cfg(pytester, tmp_path_factory):
    """test default config values"""
    src = cleandoc(
    """
        def test_cmd_config(request):
            plugin = request.config.pluginmanager.getplugin("tmux")
            tmux_cfg = plugin.getconfig(request=request)
            assert tmux_cfg['debug'] == False
            assert tmux_cfg['socket_path'] == '{}'
            assert tmux_cfg['config_file'] == None
            assert tmux_cfg['colors'] == None
            assert tmux_cfg['start_directory'] == None
            assert tmux_cfg['window_command'] == None
            assert tmux_cfg['window_width'] == None
            assert tmux_cfg['window_height'] == None
            assert tmux_cfg['assert_timeout'] == 2
            assert tmux_cfg['assert_delay'] == 0.5
    """
    ).format(
        "{}/basetemp/tmux.socket".format(str(tmp_path_factory.getbasetemp())),
    )
    pytester.makepyfile(src)
    result = pytester.runpytest()
    assert result.ret == 0

def test_cmd_cfg(pytester):
    """test config through command line arguments"""
    cmd_options = [
        "--tmux-debug",
        "--tmux-socket-path", "{}/tmux.socket".format(pytester.path),
        "--tmux-config-file", "{}/tmux.cfg".format(pytester.path),
        "--tmux-colors", "256",
        "--tmux-start-directory" , "{}".format(pytester.path),
        "--tmux-window-command", "/bin/sh",
        "--tmux-window-width", "32",
        "--tmux-window-height", "32",
        "--tmux-assert-timeout", "5",
        "--tmux-assert-delay", "1",
    ]
    src = cleandoc(
        """
        def test_cmd_config(request):
            plugin = request.config.pluginmanager.getplugin("tmux")
            tmux_cfg = plugin.getconfig(request=request)
            assert tmux_cfg['debug'] == True
            assert tmux_cfg['socket_path'] == '{}'
            assert tmux_cfg['config_file'] == '{}'
            assert tmux_cfg['colors'] == 256
            assert tmux_cfg['start_directory'] == '{}'
            assert tmux_cfg['window_command'] == '/bin/sh'
            assert tmux_cfg['window_width'] == 32
            assert tmux_cfg['window_height'] == 32
            assert tmux_cfg['assert_timeout'] == 5
            assert tmux_cfg['assert_delay'] == 1
    """
    ).format(
        "{}/tmux.socket".format(pytester.path),
        "{}/tmux.cfg".format(pytester.path),
        "{}".format(pytester.path),
    )

    pytester.makepyfile(src)
    result = pytester.runpytest(*cmd_options)
    assert result.ret == 0


def test_env_cfg(pytester, monkeypatch):
    """test config through env variables"""
    monkeypatch.setenv('PYTEST_TMUX_DEBUG', '1')
    monkeypatch.setenv('PYTEST_TMUX_SOCKET_PATH', "{}/tmux.socket_env".format(pytester.path))
    monkeypatch.setenv('PYTEST_TMUX_CONFIG_FILE', "{}/tmux.cfg_env".format(pytester.path))
    monkeypatch.setenv('PYTEST_TMUX_COLORS', '8')
    monkeypatch.setenv('PYTEST_TMUX_START_DIRECTORY', '/tmp')
    monkeypatch.setenv('PYTEST_TMUX_WINDOW_COMMAND', '/usr/bin/env')
    monkeypatch.setenv('PYTEST_TMUX_WINDOW_WIDTH', '34')
    monkeypatch.setenv('PYTEST_TMUX_WINDOW_HEIGHT', '34')
    monkeypatch.setenv('PYTEST_TMUX_ASSERT_TIMEOUT', '12')
    monkeypatch.setenv('PYTEST_TMUX_ASSERT_DELAY', '3')
    src = cleandoc(
    """
        import os
        def test_cmd_config(request, monkeypatch):
            plugin = request.config.pluginmanager.getplugin("tmux")
            tmux_cfg = plugin.getconfig(request=request)
            assert tmux_cfg['debug'] == True
            assert tmux_cfg['socket_path'] == os.environ['PYTEST_TMUX_SOCKET_PATH']
            assert tmux_cfg['config_file'] == os.environ['PYTEST_TMUX_CONFIG_FILE']
            assert tmux_cfg['colors'] == int(os.environ['PYTEST_TMUX_COLORS'])
            assert tmux_cfg['start_directory'] == os.environ['PYTEST_TMUX_START_DIRECTORY']
            assert tmux_cfg['window_command'] == os.environ['PYTEST_TMUX_WINDOW_COMMAND']
            assert tmux_cfg['window_width'] == int(os.environ['PYTEST_TMUX_WINDOW_WIDTH'])
            assert tmux_cfg['window_height'] == int(os.environ['PYTEST_TMUX_WINDOW_HEIGHT'])
            assert tmux_cfg['assert_timeout'] == int(os.environ['PYTEST_TMUX_ASSERT_TIMEOUT'])
            assert tmux_cfg['assert_delay'] == int(os.environ['PYTEST_TMUX_ASSERT_DELAY'])
    """
    )

    pytester.makepyfile(src)
    result = pytester.runpytest()

    assert result.ret == 0


def test_marker_cfg(pytester):
    """test config through fixtures"""
    src = cleandoc(
    """
        import pytest
        @pytest.mark.tmux_cfg(
            debug=True,
            socket_path='/tmp',
            config_file='/dev/null',
            colors=9,
            start_directory='/test',
            window_command='bash',
            window_width=31,
            window_height=33,
            assert_timeout=3,
            assert_delay=3
        )
        def test_cmd_config(request):
            plugin = request.config.pluginmanager.getplugin("tmux")
            tmux_cfg = plugin.getconfig(request=request)
            assert tmux_cfg['debug'] == True
            assert tmux_cfg['socket_path'] == '/tmp'
            assert tmux_cfg['config_file'] == '/dev/null'
            assert tmux_cfg['colors'] == 9
            assert tmux_cfg['start_directory'] == '/test'
            assert tmux_cfg['window_command'] == 'bash'
            assert tmux_cfg['window_width'] == 31
            assert tmux_cfg['window_height'] == 33
            assert tmux_cfg['assert_timeout'] == 3
            assert tmux_cfg['assert_delay'] == 3
    """
    )
    pytester.makepyfile(src)
    result = pytester.runpytest()
    assert result.ret == 0
