#!/usr/bin/env python#
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from pytest_tmux.fixtures import (
    _tmux_server,
    tmux,
    tmux_assertion_config,
    tmux_server_config,
    tmux_session_config,
)
from pytest_tmux.rewrite import tmux_rewrite

(tmux, _tmux_server, tmux_server_config, tmux_session_config, tmux_assertion_config)

if TYPE_CHECKING:
    from typing import List, Optional

    import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("tmux")
    group.addoption(
        "--tmux-debug",
        dest="tmux_debug",
        action="store_true",
        default=os.getenv("PYTEST_TMUX_DEBUG", False) in ("True", "1"),
        help="""
            Prompt the user to press enter during tests who use tmux ficture.
            Env: PYTEST_TMUX_DEBUG
        """,
    )
    group.addoption(
        "--tmux-socket-path",
        dest="tmux_socket_path",
        action="store",
        default=os.getenv("PYTEST_TMUX_SOCKET_PATH", None),
        help="""
            Socket path to use with libtmux.Server
            Default: [pytest_temp_dir]/tmux.socket
            Env: PYTEST_TMUX_SOCKET_PATH
        """,
    )
    group.addoption(
        "--tmux-config-file",
        dest="tmux_config_file",
        action="store",
        default=os.getenv("PYTEST_TMUX_CONFIG_FILE", None),
        help="""
            Path to a tmux configuration file to use with libtmux.Server
            Default: None
            Env: PYTEST_TMUX_CONFIG_FILE
        """,
    )
    group.addoption(
        "--tmux-colors",
        dest="tmux_colors",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_COLORS", None),
        help="""
            Number of colors to use with libtmux.Server
            Default: None
            Env: PYTEST_TMUX_COLORS
        """,
    )
    group.addoption(
        "--tmux-start-directory",
        dest="tmux_start_directory",
        action="store",
        default=os.getenv("PYTEST_TMUX_START_DIRECTORY", None),
        help="""
            Working directory in which the new window is created
            Default: None
            Env: PYTEST_TMUX_START_DIRECTORY
        """,
    )
    group.addoption(
        "--tmux-window-command",
        dest="tmux_window_command",
        action="store",
        default=os.getenv("PYTEST_TMUX_WINDOW_COMMAND", None),
        help="""
            Command executed when starting the session.
            Default: None
            Env: PYTEST_TMUX_WINDOW_COMMAND
        """,
    )
    group.addoption(
        "--tmux-window-width",
        dest="tmux_window_width",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_WINDOW_WIDTH", None),
        help="""
            Force tmux window width
            Default: None
            Env: PYTEST_TMUX_WINDOW_WIDTH
        """,
    )
    group.addoption(
        "--tmux-window-height",
        dest="tmux_window_height",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_WINDOW_HEIGHT", None),
        help="""
            Force tmux window height
            Default: None
            Env: PYTEST_TMUX_WINDOW_HEIGHT
        """,
    )
    group.addoption(
        "--tmux-assertion-timeout",
        dest="tmux_assertion_timeout",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_ASSERTION_TIMEOUT", None),
        help="""
            Seconds before tmux assertion should fail
            Default: 2
            Env: PYTEST_TMUX_ASSERTION_TIMEOUT
        """,
    )
    group.addoption(
        "--tmux-assertion-delay",
        dest="tmux_assertion_delay",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_ASSERTION_DELAY", None),
        help="""
            Seconds to wait before tmux assertion should retry
            Default: 0.5
            Env: PYTEST_TMUX_ASSERTION_DELAY
        """,
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "tmux_cfg(**cfg_opts): Allow change tmux fixtures options for the current test",
    )
    assert config.pluginmanager.register(PyTestTmuxPlugin(config), "tmux")


class PyTestTmuxPlugin:
    def __init__(self, config: pytest.Config) -> None:
        self.config = config


def pytest_assertrepr_compare(
    op: str, left: object, right: object
) -> Optional[List[str]]:
    if type(left).__name__ == "TmuxOutput" or type(right).__name__ == "TmuxOutput":
        return tmux_rewrite(op, left, right)
    else:
        return None
