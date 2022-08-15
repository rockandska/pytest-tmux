import pytest


@pytest.fixture(scope="session")
def tmux_server(request):
    plugin = request.config.pluginmanager.getplugin("tmux")
    tmux_server = plugin.server()

    yield tmux_server

    if tmux_server:
        tmux_server.kill_server()


@pytest.fixture()
def tmux(request, tmux_server):
    plugin = request.config.pluginmanager.getplugin("tmux")
    tmux_cfg = plugin.getconfig(request=request)
    tmux_client = plugin.client(tmux_server, request, **tmux_cfg)

    yield tmux_client

    if tmux_client:
        if tmux_client.session:
            tmux_client.kill_session()
