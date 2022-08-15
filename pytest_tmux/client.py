from inspect import cleandoc

from .output import TmuxOutput


class Client:
    __allowed_params = [
        "session_name",
        "start_directory",
        "window_name",
        "window_command",
        "window_height",
        "window_width",
        "assert_timeout",
        "assert_delay",
        "debug",
    ]

    @classmethod
    def list_params(cls):
        return cls.__allowed_params

    def __init__(self, tmux_server=None, pytest_request=None, **kwargs):
        self.pytest_request = pytest_request
        self._config = {}
        for x in self.__class__.__allowed_params:
            self._config[x] = kwargs.get(x, None)

        self._server = tmux_server
        self._session = None
        self._window = None
        self._pane = None
        self._config["session_name"] = pytest_request.module.__name__
        self._config["session_name"] = self._config["session_name"].replace(".", " ")
        self._config["session_name"] = self._config["session_name"].replace(":", " ")
        self._config["window_name"] = self.pytest_request.node.name
        self._previous_config = dict(self._config)

    class suspend_capture:
        def __init__(self, pytestconfig=None):
            self.capmanager = pytestconfig.pluginmanager.getplugin("capturemanager")

        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            try:
                input("Press enter to continue....")
            except KeyboardInterrupt:
                self.capmanager.resume_global_capture()

    def __debug(self, msg=None):

        if self.config["debug"]:
            with self.suspend_capture(self.pytest_request.config):
                print("")
                print(cleandoc(msg))

    @property
    def config(self):
        return self._config

    @property
    def previous_config(self):
        return self._previous_config

    def set(self, **kwargs):
        self._previous_config = dict(self._config)
        self._config.update(kwargs)

    def restore_previous_config(self):
        self._config = dict(self._previous_config)

    @property
    def session(self):
        if self._session is None:
            self.__debug("PyTestTmuxPlugin started with DEBUG")

            self._session = self.server.new_session(
                session_name=self.config["session_name"],
                window_name=self.config["window_name"],
                window_command=self.config["window_command"],
            )

            if self.config["window_width"]:
                self.window.set_window_option(
                    "force-width", self.config["window_width"]
                )

            if self.config["window_height"]:
                self.window.set_window_option(
                    "force-height", self.config["window_height"]
                )

            self.__debug(
                """
                        Open a new window terminal and use the bellow command to connect to the tmux session
                        tmux -S "{}" attach -t "{}"
                        """.format(
                    self.server.socket_path, self.config["session_name"]
                )
            )

        return self._session

    @property
    def window(self):
        if self._window is None:
            self._window = self.session.attached_window
        return self._window

    @property
    def pane(self):
        if self._pane is None:
            self._pane = self.window.attached_pane
        return self._pane

    @property
    def server(self):
        return self._server

    def kill_session(self):
        self.__debug(
            """
                    killing the session "{}"
                    """.format(
                self.session._info["session_name"]
            )
        )
        self.session.kill_session()

    def clear(self):
        self.pane.clear()

    def send_keys(self, cmd=None, **kwargs):
        if "supress_history" not in kwargs:
            kwargs["suppress_history"] = False
        self.__debug(
            """
                    Send "{}" to tmux session
                    """.format(
                cmd
            )
        )
        self.pane.send_keys(cmd, **kwargs)

    def screen(self, timeout=None, delay=None):
        if timeout is None:
            timeout = self.config["assert_timeout"]
        if delay is None:
            delay = self.config["assert_delay"]

        def _capture():
            return "\n".join(self.pane.capture_pane())

        return TmuxOutput(_capture, timeout=timeout, delay=delay)

    def row(self, row, timeout=None, delay=None):
        if not isinstance(row, int):
            raise TypeError("row should be an integer")

        if timeout is None:
            timeout = self.config["assert_timeout"]
        if delay is None:
            delay = self.config["assert_delay"]

        def _capture():
            try:
                output = self.pane.capture_pane()[row]
            except IndexError:
                output = ""
            return output

        return TmuxOutput(_capture, timeout=timeout, delay=delay)
