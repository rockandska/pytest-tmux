import pytest

from pytest_tmux.client import TmuxClient


@pytest.fixture(scope="session")
def tmux_server_config():
    """
    Fixture used to override default configuration for libtmux.Server
    """
    return {}


@pytest.fixture()
def tmux_session_config():
    """
    Fixture used to override default configuration for libtmux.Server.new_session
    """
    return {}


@pytest.fixture()
def tmux_assertion_config():
    """
    Fixture used to override default configuration for pytest_tmux.output.TmuxOutput
    """
    return {}


@pytest.fixture(scope="session")
def _tmux_server(tmpdir_factory, request, pytestconfig, tmux_server_config):

    tmux_server = TmuxClient(
        tmpdir_factory=tmpdir_factory,
        request=request,
        pytestconfig=pytestconfig,
        server_cfg_fixture=tmux_server_config,
    )

    yield tmux_server

    if tmux_server.server:
        tmux_server.server.kill_server()


@pytest.fixture()
def tmux(
    tmpdir_factory,
    request,
    pytestconfig,
    _tmux_server,
    tmux_session_config,
    tmux_assertion_config,
):

    tmux_client = TmuxClient(
        request=request,
        pytestconfig=pytestconfig,
        tmpdir_factory=tmpdir_factory,
        server=_tmux_server.server,
        server_cfg_fixture=_tmux_server._server_cfg_fixture,
        session_cfg_fixture=tmux_session_config,
        assertion_cfg_fixture=tmux_assertion_config,
    )

    yield tmux_client

    if tmux_client:
        if tmux_client.sessions > 0:
            tmux_client.debug(
                """
                Closing session
                """
            )
            tmux_client.session.kill_session()
