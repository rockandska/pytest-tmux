import inspect
import os

import pytest

pytest_plugins = "pytester"


@pytest.fixture
def options(testdir):

    return PyTestOptions(testdir)


class PyTestOptions:
    def __init__(self, testdir):
        self.cmd_options = {
            "tmux_debug": {
                "value": True,
                "env": "PYTEST_TMUX_DEBUG",
                "cmd": "--tmux-debug",
            },
            "tmux_socket_path": {
                "value": "{}/tmux.socket".format(str(testdir.tmpdir)),
                "env": "PYTEST_TMUX_SOCKET_PATH",
                "cmd": "--tmux-socket-path",
            },
            "tmux_config_file": {
                "value": "{}/tmux.cfg".format(str(testdir.tmpdir)),
                "env": "PYTEST_TMUX_CONFIG_FILE",
                "cmd": "--tmux-config-file",
            },
            "tmux_colors": {
                "value": 256,
                "env": "PYTEST_TMUX_COLORS",
                "cmd": "--tmux-colors",
            },
            "tmux_start_directory": {
                "value": str(testdir.tmpdir),
                "env": "PYTEST_TMUX_START_DIRECTORY",
                "cmd": "--tmux-start-directory",
            },
            "tmux_window_command": {
                "value": "/bin/sh",
                "env": "PYTEST_TMUX_WINDOW_COMMAND",
                "cmd": "--tmux-window-command",
            },
            "tmux_window_width": {
                "value": 80,
                "env": "PYTEST_TMUX_WINDOW_WIDTH",
                "cmd": "--tmux-window-width",
            },
            "tmux_window_height": {
                "value": 40,
                "env": "PYTEST_TMUX_WINDOW_HEIGHT",
                "cmd": "--tmux-window-height",
            },
            "tmux_assert_timeout": {
                "value": 10,
                "env": "PYTEST_TMUX_ASSERT_TIMEOUT",
                "cmd": "--tmux-assert-timeout",
            },
            "tmux_assert_delay": {
                "value": 5,
                "env": "PYTEST_TMUX_ASSERT_DELAY",
                "cmd": "--tmux-assert-delay",
            },
        }

        with open(self.cmd_options["tmux_config_file"]["value"], "w") as f:
            f.write("set -g status off")

    def options_setenv(self, arg):
        opt = getattr(self, arg)
        for k in opt.keys():
            os.environ[opt[k]["env"]] = str(opt[k]["value"])

    def options_unsetenv(self, arg):
        opt = getattr(self, arg)
        for k in opt.keys():
            os.environ.pop(opt[k]["env"], None)

    def options2arg(self, arg):
        result = []
        opt = getattr(self, arg)
        for k in opt.keys():
            if isinstance(opt[k]["value"], bool) is False:
                result.append("{}={}".format(opt[k]["cmd"], opt[k]["value"]))
            else:
                result.append("{}".format(opt[k]["cmd"]))
        return result

    def options2dict(self, arg):
        result = {}
        opt = getattr(self, arg)
        for k in opt.keys():
            short_k = k[5:]
            result[short_k] = opt[k]["value"]
        return result

    def printtest(self):
        src = inspect.cleandoc(
            """
            def test_cmd_config(request):
                plugin = request.config.pluginmanager.getplugin("tmux")
                tmux_cfg = plugin.getconfig(request=request)
                assert tmux_cfg['debug'] == {}
                assert tmux_cfg['socket_path'] == '{}'
                assert tmux_cfg['config_file'] == '{}'
                assert tmux_cfg['colors'] == {}
                assert tmux_cfg['start_directory'] == '{}'
                assert tmux_cfg['window_command'] == '{}'
                assert tmux_cfg['window_width'] == {}
                assert tmux_cfg['window_height'] == {}
                assert tmux_cfg['assert_timeout'] == {}
                assert tmux_cfg['assert_delay'] == {}
        """
        ).format(
            self.cmd_options["tmux_debug"]["value"],
            self.cmd_options["tmux_socket_path"]["value"],
            self.cmd_options["tmux_config_file"]["value"],
            self.cmd_options["tmux_colors"]["value"],
            self.cmd_options["tmux_start_directory"]["value"],
            self.cmd_options["tmux_window_command"]["value"],
            self.cmd_options["tmux_window_width"]["value"],
            self.cmd_options["tmux_window_height"]["value"],
            self.cmd_options["tmux_assert_timeout"]["value"],
            self.cmd_options["tmux_assert_delay"]["value"],
        )

        return src

    def printmarkertest(self):
        src = inspect.cleandoc(
            """
            import pytest
            @pytest.mark.tmux_cfg(**{})
        """
        ).format(self.options2dict("cmd_options"))

        return src + "\n" + self.printtest()
