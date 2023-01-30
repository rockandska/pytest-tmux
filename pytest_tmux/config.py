from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from typing import Any, Dict, Iterator, Optional, Union

    import pytest


class TmuxConfig(Mapping[str, str]):
    """
    Create a config instance.

    Args:
        request: a pytest request fixture object
        pytestconfig: a pytest pytestconfig fixture object
        tmpdir_factory: a pytest tmpdir_factory fixture object
        server_cfg_fixture: a server config dictionary
        session_cfg_fixture: a session config dictionary
        assertion_cfg_fixture: a assertion config dictionary

    Attributes:
        server: a [TmuxConfigServer][pytest_tmux.config.TmuxConfigServer] instance
        session: a [TmuxConfigSession][pytest_tmux.config.TmuxConfigSession] instance
        assertion: a [TmuxConfigAssert][pytest_tmux.config.TmuxConfigAssert] instance
        plugin: a [TmuxConfigPlugin][pytest_tmux.config.TmuxConfigPlugin] instance
    """

    def __init__(
        self,
        request: Optional[pytest.FixtureRequest] = None,
        pytestconfig: Optional[pytest.Config] = None,
        tmpdir_factory: Optional[pytest.TempdirFactory] = None,
        server_cfg_fixture: Optional[Dict[str, Union[str, int]]] = None,
        session_cfg_fixture: Optional[Dict[str, Union[str, int]]] = None,
        assertion_cfg_fixture: Optional[Dict[str, Union[str, int]]] = None,
    ) -> None:
        super().__setattr__("_config", {})
        super().__setattr__("_request", request)
        super().__setattr__("_tmpdir_factory", tmpdir_factory)
        super().__setattr__("_pytestconfig", pytestconfig)
        super().__setattr__("_server_cfg_fixture", server_cfg_fixture)
        super().__setattr__("_session_cfg_fixture", session_cfg_fixture)
        super().__setattr__("_assertion_cfg_fixture", assertion_cfg_fixture)
        self._default()

    def _default(self) -> None:
        assert isinstance(self._config, dict)
        self._config.update({})

    def __getattr__(self, key: str) -> str:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._request, pytest.FixtureRequest)
            assert isinstance(self._pytestconfig, pytest.Config)
            assert isinstance(self._tmpdir_factory, pytest.TempdirFactory)
            assert isinstance(self._server_cfg_fixture, dict)
            assert isinstance(self._session_cfg_fixture, dict)
            assert isinstance(self._assertion_cfg_fixture, dict)
            assert isinstance(self._pytestconfig, pytest.Config)
        if self._config.get(key, None) is None:
            if key == "server":
                self._config[key] = TmuxConfigServer(
                    tmpdir_factory=self._tmpdir_factory,
                    pytestconfig=self._pytestconfig,
                    server_cfg_fixture=self._server_cfg_fixture,
                )
            elif key == "session":
                self._config[key] = TmuxConfigSession(
                    request=self._request,
                    pytestconfig=self._pytestconfig,
                    session_cfg_fixture=self._session_cfg_fixture,
                )
            elif key == "assertion":
                self._config[key] = TmuxConfigAssert(
                    request=self._request,
                    pytestconfig=self._pytestconfig,
                    assertion_cfg_fixture=self._assertion_cfg_fixture,
                )
            elif key == "plugin":
                self._config[key] = TmuxConfigPlugin(
                    pytestconfig=self._pytestconfig,
                )
        return self._config.get(key, None)

    def __contains__(self, other: object) -> bool:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
        return other in self._config

    def __setattr__(self, key: str, value: Any) -> None:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
        self._config[key] = value

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._config)

    def __len__(self) -> int:
        return len(self._config)


class TmuxConfigServer(TmuxConfig):
    """
    Display config value by loading settings from:
        - default
        - [tmux_server_config][pytest_tmux.fixtures.tmux_server_config] fixture
        - env
        - cmd args

    Args:
        request: a pytest request fixture object
        pytestconfig: a pytest pytestconfig fixture object
        tmpdir_factory: a pytest tmpdir_factory fixture object
        server_cfg_fixture: a server config dictionary
        session_cfg_fixture: a session config dictionary
        assertion_cfg_fixture: a assertion config dictionary

    Attributes:
        **args: All args accepted by libtmux.server.Server()
    """

    def _default(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._tmpdir_factory, pytest.TempdirFactory)
        self._config.update(
            {"socket_path": str(self._tmpdir_factory.getbasetemp() + "/tmux.socket")}
        )
        self._config.update(self._server_cfg_fixture or {})

    def __getattr__(self, key: str) -> str:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._pytestconfig, pytest.Config)
        if self._pytestconfig.getoption("tmux_socket_path"):
            self._config["socket_path"] = self._pytestconfig.getoption(
                "tmux_socket_path"
            )
        if self._pytestconfig.getoption("tmux_config_file"):
            self._config["config_file"] = self._pytestconfig.getoption(
                "tmux_config_file"
            )
        if self._pytestconfig.getoption("tmux_colors"):
            self._config["colors"] = self._pytestconfig.getoption("tmux_colors")
        return self._config.get(key, None)


class TmuxConfigSession(TmuxConfig):
    """
    Display config value by loading settings from:
        - default
        - [tmux_session_config][pytest_tmux.fixtures.tmux_session_config] fixture
        - tmux_session_cfg marker
        - tmux.config.session.[attribute] set in tests
        - env
        - cmd args

    Args:
        request: a pytest request fixture object
        pytestconfig: a pytest pytestconfig fixture object
        session_cfg_fixture: a session config dictionary

    Attributes:
        **attrs: All args accepted by libtmux.server.Server.new_session()
    """

    def _default(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._request, pytest.FixtureRequest)
            assert isinstance(self._session_cfg_fixture, dict)
        __test_file_name = "".join(
            [c if c.isalnum() else "_" for c in self._request.module.__name__]
        )
        __test_name = "".join(
            [c if c.isalnum() else "_" for c in self._request.node.name]
        )
        self._config.update(
            {
                "session_name": "_".join([__test_file_name, __test_name]),
                "window_name": __test_name,
            }
        )

        marker = self._request.node.get_closest_marker("tmux_session_cfg")
        if marker:
            self._config.update(marker.kwargs)

        self._config.update(self._session_cfg_fixture or {})

    def __getattr__(self, key: str) -> str:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._pytestconfig, pytest.Config)
        if self._pytestconfig.getoption("tmux_start_directory"):
            self._config["start_directory"] = self._pytestconfig.getoption(
                "tmux_start_directory"
            )
        if self._pytestconfig.getoption("tmux_window_command"):
            self._config["window_command"] = self._pytestconfig.getoption(
                "tmux_window_command"
            )
        if self._pytestconfig.getoption("tmux_window_width"):
            self._config["x"] = self._pytestconfig.getoption("tmux_window_width")
        if self._pytestconfig.getoption("tmux_window_height"):
            self._config["y"] = self._pytestconfig.getoption("tmux_window_height")
        return self._config.get(key, None)


class TmuxConfigAssert(TmuxConfig):
    """
    Display config value by loading settings from:
        - default
        - [tmux_assertion_config][pytest_tmux.fixtures.tmux_assertion_config] fixture
        - tmux_assertion_cfg marker
        - tmux.config.assertion.[attribute] set in tests
        - env
        - cmd args

    Args:
        request: a pytest request fixture object
        pytestconfig: a pytest pytestconfig fixture object
        assertion_cfg_fixture: a assertion config dictionary

    Attributes:
        **attrs: All args accepted by :

          - [pytest_tmux.client.TmuxClient.screen][pytest_tmux.client.TmuxClient.screen]
          - [pytest_tmux.client.TmuxClient.row][pytest_tmux.client.TmuxClient.row]
    """

    def _default(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._assertion_cfg_fixture, dict)
            assert isinstance(self._request, pytest.FixtureRequest)
        self._config.update({"timeout": 2, "delay": 0.5})
        self._config.update(self._assertion_cfg_fixture or {})
        marker = self._request.node.get_closest_marker("tmux_assertion_cfg")
        if marker:
            self._config.update(marker.kwargs)

    def __getattr__(self, key: str) -> str:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._pytestconfig, pytest.Config)
        if self._pytestconfig.getoption("tmux_assertion_timeout"):
            self._config["timeout"] = self._pytestconfig.getoption(
                "tmux_assertion_timeout"
            )
        if self._pytestconfig.getoption("tmux_assertion_delay"):
            self._config["delay"] = self._pytestconfig.getoption("tmux_assertion_delay")
        return self._config.get(key, None)


class TmuxConfigPlugin(TmuxConfig):
    """
    Display config value by loading settings from:
        - default
        - tmux.config.plugin.[attribute] set in tests
        - env
        - cmd args

    Args:
        request: a pytest request fixture object
        pytestconfig: a pytest pytestconfig fixture object

    Attributes:
        debug (bool):  pytest-tmux debug setting
    """

    def _default(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
        self._config.update({"debug": False})

    def __getattr__(self, key: str) -> str:
        if TYPE_CHECKING:
            assert isinstance(self._config, dict)
            assert isinstance(self._pytestconfig, pytest.Config)
        if self._pytestconfig.getoption("tmux_debug"):
            self._config["debug"] = self._pytestconfig.getoption("tmux_debug")
        return self._config.get(key, None)
