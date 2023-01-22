from collections.abc import Mapping


class TmuxConfig(Mapping):
    def __init__(
        self,
        request=None,
        pytestconfig=None,
        tmpdir_factory=None,
        server_cfg_fixture=None,
        session_cfg_fixture=None,
        assertion_cfg_fixture=None,
    ):
        super().__setattr__("_config", {})
        super().__setattr__("_request", request)
        super().__setattr__("_tmpdir_factory", tmpdir_factory)
        super().__setattr__("_pytestconfig", pytestconfig)
        super().__setattr__("_server_cfg_fixture", server_cfg_fixture)
        super().__setattr__("_session_cfg_fixture", session_cfg_fixture)
        super().__setattr__("_assertion_cfg_fixture", assertion_cfg_fixture)
        self._default()

    def _default(self):
        return {}

    def __getattr__(self, key):
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

    def __contains__(self, other):
        return other in self._config

    def __setattr__(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)


class TmuxConfigServer(TmuxConfig):
    def _default(self):
        self._config.update(
            {"socket_path": str(self._tmpdir_factory.getbasetemp() + "/tmux.socket")}
        )
        self._config.update(self._server_cfg_fixture or {})

    def __getattr__(self, key):
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
    def _default(self):
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

    def __getattr__(self, key):
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
    def _default(self):
        self._config.update({"timeout": 2, "delay": 0.5})
        self._config.update(self._assertion_cfg_fixture or {})
        marker = self._request.node.get_closest_marker("tmux_assertion_cfg")
        if marker:
            self._config.update(marker.kwargs)

    def __getattr__(self, key):
        if self._pytestconfig.getoption("tmux_assertion_timeout"):
            self._config["timeout"] = self._pytestconfig.getoption(
                "tmux_assertion_timeout"
            )
        if self._pytestconfig.getoption("tmux_assertion_delay"):
            self._config["delay"] = self._pytestconfig.getoption("tmux_assertion_delay")
        return self._config.get(key, None)


class TmuxConfigPlugin(TmuxConfig):
    def _default(self):
        self._config.update({"debug": False})

    def __getattr__(self, key):
        if self._pytestconfig.getoption("tmux_debug"):
            self._config["debug"] = self._pytestconfig.getoption("tmux_debug")
        return self._config.get(key, None)
