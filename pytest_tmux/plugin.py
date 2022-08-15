#!/usr/bin/env python#
import os

from libtmux import Server

from pytest_tmux.client import Client
from pytest_tmux.fixtures import tmux, tmux_server
from pytest_tmux.rewrite import tmux_rewrite

(tmux_server, tmux)


def pytest_addoption(parser):
    """Add options to control tmux tests"""
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
        "--tmux-assert-timeout",
        dest="tmux_assert_timeout",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_ASSERT_TIMEOUT", 2),
        help="""
            Seconds before tmux assertion should fail
            Default: 2
            Env: PYTEST_TMUX_ASSERT_TIMEOUT
        """,
    )
    group.addoption(
        "--tmux-assert-delay",
        dest="tmux_assert_delay",
        type=int,
        action="store",
        default=os.getenv("PYTEST_TMUX_ASSERT_DELAY", 0.5),
        help="""
            Seconds to wait before tmux assertion should retry
            Default: 0.5
            Env: PYTEST_TMUX_ASSERT_DELAY
        """,
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "tmux_cfg(**cfg_opts): Allow change tmux fixtures options for the current test",
    )
    assert config.pluginmanager.register(PyTestTmuxPlugin(config), "tmux")


class PyTestTmuxPlugin:
    def __init__(self, config):
        self.config = config

    def getconfig(self, config=None, request=None, **kwargs):
        tmux_cfg = {}
        """ Global/Session config """
        if config is not None:
            tmux_cfg.update(self._load_tmux_config(config))
        else:
            tmux_cfg.update(self._load_tmux_config(self.config))
        """ Test / Marker config """
        if request is not None:
            tmux_cfg.update(self._load_markers_config(request))
        tmux_cfg.update(kwargs)

        """
        Set defaults who can't be set by pytest_addoption
        """
        if tmux_cfg["socket_path"] is None:
            tmux_cfg["socket_path"] = (
                self.config._tmpdirhandler.getbasetemp() + "/tmux.socket"
            )

        return tmux_cfg

    def _load_tmux_config(self, config):
        """Load configuration from '--tmux-*' command-line."""
        cfg = {}
        for k, v in vars(config.option).items():
            if k.startswith("tmux_"):
                short_key = k[5:]
                cfg[short_key] = v

        return cfg

    def _load_markers_config(self, request):
        """Load configuration from 'tmux_cfg' markers."""
        cfg = {}

        marker = request.node.get_closest_marker("tmux_cfg")
        if marker:
            cfg = marker.kwargs

        return cfg

    def server(self):
        """
        Return a libtmux.Server object (use by tmux_server session fixture)
        """
        tmux_server_cfg = {}
        tmux_cfg = self.getconfig()
        tmux_server_keys = ["socket_path", "config_file", "colors"]
        for k, v in tmux_cfg.items():
            if k in tmux_server_keys:
                if v is not None:
                    tmux_server_cfg[k] = v

        return Server(**tmux_server_cfg)

    def client(self, tmux_server, pytest_request, **kwargs):
        """
        Return a pytest_tmux.Client object (used by tmux function fixture)
        """

        if not isinstance(tmux_server, Server):
            raise ValueError("First arg need to be a Server instance")

        if type(pytest_request).__name__ != "SubRequest":
            raise ValueError("Second argument need to be a SubRequest instance")

        tmux_client_cfg = {}
        tmux_cfg = kwargs
        """
        Retrieve allowed parameters for Client class
        Then filtering config parameters to use
        """
        tmux_client_keys = Client.list_params()

        for k, v in tmux_cfg.items():
            if k in tmux_client_keys:
                if v is not None:
                    tmux_client_cfg[k] = v

        return Client(
            tmux_server=tmux_server, pytest_request=pytest_request, **tmux_client_cfg
        )


def pytest_assertrepr_compare(op, left, right):
    if type(left).__name__ == "TmuxOutput" or type(right).__name__ == "TmuxOutput":
        return tmux_rewrite(op, left, right)
