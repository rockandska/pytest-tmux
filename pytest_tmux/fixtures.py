import pytest

from pytest_tmux.client import TmuxClient


@pytest.fixture(scope="session")
def tmux_server_config():
    """
    Fixture intended to be override by the user to update default tmux server config

    Scope : session

    Returns:
        a dictionnary containing args for libtmux.server.Server
    """
    return {}


@pytest.fixture()
def tmux_session_config():
    """
    Fixture intended to be override by the user to update default tmux session
    config.

    Scope: function

    Returns:
        a dictionnary containing args for libtmux.server.Server.new_session()
    """
    return {}


@pytest.fixture()
def tmux_assertion_config():
    """
    Fixture intended to be override by the user to update default tmux assertion config

    Scope: function

    Returns:
        a dictionnary containing args for :

          - pytest_tmux.client.TmuxClient.screen()
          - pytest_tmux.client.TmuxClient.row()
    """
    return {}


@pytest.fixture(scope="session")
def _tmux_server(tmpdir_factory, request, pytestconfig, tmux_server_config):
    """
    Fixture used to create a server for the whole session

    Scope: function

    Returns:
        A [pytest_tmux.client.TmuxClient][pytest_tmux.client.TmuxClient] object
    """

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
    """
    Fixture intended to be used with tmux tests

    Scope: function

    Returns:
        A [pytest_tmux.client.TmuxClient][pytest_tmux.client.TmuxClient] object
    """

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
