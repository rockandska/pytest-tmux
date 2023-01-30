# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def test_help_message(pytester: pytest.Pytester) -> None:
    result = pytester.runpytest(
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
            "  --tmux-assertion-timeout=TMUX_ASSERTION_TIMEOUT",
            "  --tmux-assertion-delay=TMUX_ASSERTION_DELAY",
        ]
    )
