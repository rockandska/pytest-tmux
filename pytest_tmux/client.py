from __future__ import annotations

from inspect import cleandoc
from typing import TYPE_CHECKING

from libtmux.pane import Pane as TmuxPane
from libtmux.server import Server as TmuxServer
from pytest import exit as Exit

from pytest_tmux.config import TmuxConfig
from pytest_tmux.output import TmuxOutput

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union

    import libtmux
    import pytest

    from pytest_tmux.config import (
        TmuxConfigAssert,
        TmuxConfigPlugin,
        TmuxConfigServer,
        TmuxConfigSession,
    )


class TmuxClient:
    """
    When instantiated:
        - create/stores link to :
            - libtmux.server.Server instance
            - libtmux.session.Session instance
            - libtmux.window.Window instance
            - libtmux.pane.Pane instance
        - create some methods specific to pytest-tmux
        - create a [pytest_tmux.config.TmuxConfig][pytest_tmux.config.TmuxConfig] instance

    Args:
        request: a pytest request fixture object
        pytestconfig: a pytest pytestconfig fixture object
        tmpdir_factory: a pytest tmpdir_factory fixture object
        server: a libtmux.server.server object
        server_cfg_fixture: a server config dictionary
        session_cfg_fixture: a session config dictionary
        assertion_cfg_fixture: a assertion config dictionary
    """

    def __init__(
        self,
        request: pytest.FixtureRequest,
        pytestconfig: pytest.Config,
        tmpdir_factory: Optional[pytest.TempdirFactory] = None,
        server: Optional[TmuxServer] = None,
        server_cfg_fixture: Optional[Dict[str, Union[str, int]]] = None,
        session_cfg_fixture: Optional[Dict[str, Union[str, int]]] = None,
        assertion_cfg_fixture: Optional[Dict[str, Union[str, int]]] = None,
    ) -> None:
        """State"""
        self._server = server
        self._session = None  # type: Optional[ libtmux.session.Session ]
        self._window = None  # type: Optional[ libtmux.window.Window ]
        self._pane = None  # type: Optional[ libtmux.pane.Pane ]
        self._debug = None  # type: Optional[ bool ]
        self._interrupted = False
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
        def __init__(
            self, request: pytest.FixtureRequest, interrupted: bool = False
        ) -> None:
            self.capmanager = request.config.pluginmanager.getplugin("capturemanager")
            self.interrupted = interrupted

        def __enter__(self) -> None:
            self.capmanager.suspend_global_capture(in_=True)

        def __exit__(self, _1: Any, _2: Any, _3: Any) -> None:
            try:
                if not self.interrupted:
                    input("Press enter to continue....")
            except OSError:
                pass
            finally:
                self.capmanager.resume_global_capture()

    def debug(self, msg: str) -> None:
        """
        Display a message and ask to press enter when pytest-tmux debug is
        activated.

        On first call, display a command who let the user been attached to the
        test session.

        Args:
            msg:    The message to display
        """
        if TYPE_CHECKING:
            assert isinstance(self.config, TmuxConfig)
            assert isinstance(self.config.plugin, TmuxConfigPlugin)
        if self.config.plugin.debug:
            try:
                if self._debug is None:
                    with self.suspend_capture(self._request):
                        assert isinstance(self.pane, TmuxPane)
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
                with self.suspend_capture(self._request, self._interrupted):
                    print("")
                    print(cleandoc(msg))
            except KeyboardInterrupt:
                self._interrupted = True
                Exit("CTRL+C detected.")

    @property
    def session(self) -> libtmux.session.Session:
        """
        A direct link to libtmux.session.Session created for the actual test.

        The object is created on the first call who need it.

        Returns:
            a libtmux.session.Session object
        """
        if TYPE_CHECKING:
            assert isinstance(self.config, TmuxConfig)
            assert isinstance(self.config.session, TmuxConfigSession)
        if self._session is None:
            self._session = self.server.new_session(**self.config.session)
            self.sessions += 1

        return self._session

    @property
    def window(self) -> libtmux.window.Window:
        """
        A direct link to libtmux.window.Window created for the actual test.

        The object is created on the first call who need it.

        Returns:
            a libtmux.window.Window object
        """
        if self._window is None:
            self._window = self.session.attached_window
        return self._window

    @property
    def pane(self) -> Optional[libtmux.pane.Pane]:
        """
        A direct link to libtmux.pane.Pane created for the actual test.

        The object is created on the first call who need it.

        Returns:
            a libtmux.pane.Pane object
        """
        if self._pane is None:
            self._pane = self.window.attached_pane

        return self._pane

    @property
    def server(self) -> libtmux.server.Server:
        """
        A direct link to libtmux.server.Server created for the actual test
        session.

        The object is created on the first call who need it.

        Returns:
            a libtmux.server.Server object
        """
        if TYPE_CHECKING:
            assert isinstance(self.config, TmuxConfig)
            assert isinstance(self.config.server, TmuxConfigServer)
        if self._server is None:
            self._server = TmuxServer(**self.config.server)
        return self._server

    def clear(self) -> None:
        """
        Shortcut for libtmux.pane.Pane.clear()
        """
        assert isinstance(self.pane, TmuxPane)
        self.pane.clear()

    def send_keys(self, cmd: str, **kwargs: Any) -> None:
        """
        Send commands to the actual pane

        Args:
            cmd: Text or input into pane
            kwargs: every arguments accepted by libtmux.pane.Pane.send_keys()
        """
        if "suppress_history" not in kwargs:
            kwargs["suppress_history"] = False
        self.debug(
            """
                    Send "{}" to tmux session
                    """.format(
                cmd
            )
        )
        assert isinstance(self.pane, TmuxPane)
        self.pane.send_keys(cmd, **kwargs)

    def screen(
        self, timeout: Optional[int] = None, delay: Optional[Union[int, float]] = None
    ) -> TmuxOutput:
        """
        Get screen content from pane with retry capability on operators

        Args:
            timeout: how long to wait for the assertion to failed
            delay: how long before retrying the assertion

        Returns:
            a [TmuxOutput][pytest_tmux.output.TmuxOutput] instance
        """

        if TYPE_CHECKING:
            assert isinstance(self.config, TmuxConfig)
            assert isinstance(self.config.server, TmuxConfigAssert)
        if timeout is None:
            timeout = self.config.assertion.timeout
        if delay is None:
            delay = self.config.assertion.delay

        self.debug(
            """
            Check tmux screen
            """
        )

        def _capture() -> str:
            assert isinstance(self.pane, TmuxPane)
            return "\n".join(self.pane.capture_pane())

        return TmuxOutput(_capture, timeout=timeout, delay=delay)

    def row(
        self,
        row: int,
        timeout: Optional[int] = None,
        delay: Optional[Union[int, float]] = None,
    ) -> TmuxOutput:
        """
        Get row content from pane with retry capability on operators

        Args:
            row: which row from libtmux.pane.Pane.capture_pane to set in [TmuxOutput][pytest_tmux.output.TmuxOutput]
            timeout: how long to wait for the assertion to failed
            delay: how long before retrying the assertion

        Returns:
            a [TmuxOutput][pytest_tmux.output.TmuxOutput] instance
        """
        if TYPE_CHECKING:
            assert isinstance(self.config, TmuxConfig)
            assert isinstance(self.config.server, TmuxConfigAssert)

        if not isinstance(row, int):
            raise TypeError("row should be an integer")

        if timeout is None:
            timeout = self.config.assertion.timeout
        if delay is None:
            delay = self.config.assertion.delay

        self.debug(
            f"""
            Check tmux row {row}
            """
        )

        def _capture() -> str:
            assert isinstance(self.pane, TmuxPane)
            try:
                output = self.pane.capture_pane()[row]
            except IndexError:
                output = ""
            return output

        return TmuxOutput(_capture, timeout=timeout, delay=delay)
