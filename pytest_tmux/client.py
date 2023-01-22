from inspect import cleandoc

from libtmux import Server

from pytest_tmux.config import TmuxConfig
from pytest_tmux.output import TmuxOutput


class TmuxClient:
    def __init__(
        self,
        request=None,
        pytestconfig=None,
        tmpdir_factory=None,
        server=None,
        server_cfg_fixture=None,
        session_cfg_fixture=None,
        assertion_cfg_fixture=None,
    ):
        """State"""
        self._server = server
        self._session = None
        self._window = None
        self._pane = None
        self._debug = None
        self.sessions = 0

        if server is None and tmpdir_factory is None:
            raise ValueError("tmpdir_factory is requiered if server is not provided")

        """ Configuration """
        self._request = request
        self._pytestconfig = pytestconfig
        self._tmpdir_factory = tmpdir_factory
        self._server_cfg_fixture = server_cfg_fixture
        self._session_cfg_fixture = session_cfg_fixture
        self._assertion_cfg_fixture = assertion_cfg_fixture

        self.config = TmuxConfig(
            request=self._request,
            pytestconfig=self._pytestconfig,
            tmpdir_factory=self._tmpdir_factory,
            server_cfg_fixture=self._server_cfg_fixture,
            session_cfg_fixture=self._session_cfg_fixture,
            assertion_cfg_fixture=self._assertion_cfg_fixture,
        )

    class suspend_capture:
        def __init__(self, request=None):
            self.capmanager = request.config.pluginmanager.getplugin("capturemanager")

        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            try:
                input("Press enter to continue....")
            except KeyboardInterrupt:
                self.capmanager.resume_global_capture()
            except OSError:
                pass

    def debug(self, msg=None):
        if self.config.plugin.debug:
            if self._debug is None:
                with self.suspend_capture(self._request):
                    print("")
                    print("")
                    print(
                        cleandoc(
                            """
                        pytest-tmux started with DEBUG

                        ****************************************************************************************
                        * Open a new window terminal and use the bellow command to connect to the tmux session *
                        ****************************************************************************************

                        tmux -S "{}" attach -t "{}" \\; setw force-width {} \\; setw force-height {}

                        """.format(
                                self.server.socket_path,
                                self.config.session.session_name,
                                self.pane.display_message(
                                    "#{window_width}", get_text=True
                                )[0],
                                self.pane.display_message(
                                    "#{window_height}", get_text=True
                                )[0],
                            )
                        )
                    )
                    print("")
                    self._debug = True
            with self.suspend_capture(self._request):
                print("")
                print(cleandoc(msg))

    @property
    def session(self):
        if self._session is None:
            self._session = self.server.new_session(**self.config.session)
            self.sessions += 1

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
        if self._server is None:
            self._server = Server(**self.config.server)
        return self._server

    def clear(self):
        self.pane.clear()

    def send_keys(self, cmd=None, **kwargs):
        if "supress_history" not in kwargs:
            kwargs["suppress_history"] = False
        self.debug(
            """
                    Send "{}" to tmux session
                    """.format(
                cmd
            )
        )
        self.pane.send_keys(cmd, **kwargs)

    def screen(self, timeout=None, delay=None):

        if timeout is None:
            timeout = self.config.assertion.timeout
        if delay is None:
            delay = self.config.assertion.timeout

        self.debug(
            """
            Check tmux screen
            """
        )

        def _capture():
            return "\n".join(self.pane.capture_pane())

        return TmuxOutput(_capture, timeout=timeout, delay=delay)

    def row(self, row, timeout=None, delay=None):
        if not isinstance(row, int):
            raise TypeError("row should be an integer")

        if timeout is None:
            timeout = self.config.assertion.timeout
        if delay is None:
            delay = self.config.assertion.timeout

        self.debug(
            f"""
            Check tmux row {row}
            """
        )

        def _capture():
            try:
                output = self.pane.capture_pane()[row]
            except IndexError:
                output = ""
            return output

        return TmuxOutput(_capture, timeout=timeout, delay=delay)
