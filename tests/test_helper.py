# -*- coding: utf-8 -*-


def test_help_message(testdir):
    result = testdir.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "tmux:",
            "  --tmux-debug *",
            "  --tmux-socket-path=TMUX_SOCKET_PATH",
            "  --tmux-config-file=TMUX_CONFIG_FILE",
            "  --tmux-colors=TMUX_COLORS",
            "  --tmux-start-directory=TMUX_START_DIRECTORY",
            "  --tmux-window-command=TMUX_WINDOW_COMMAND",
            "  --tmux-window-width=TMUX_WINDOW_WIDTH",
            "  --tmux-window-height=TMUX_WINDOW_HEIGHT",
            "  --tmux-assert-timeout=TMUX_ASSERT_TIMEOUT",
        ]
    )
