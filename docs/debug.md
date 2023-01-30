# Debug

pytest-tmux allow interative debugging by using `--tmux-debug`.

It will prompt you to :

- open the tmux session for the current test
- press enter to continue :
    - when calling `tmux.send_keys()`
    - when calling `tmux.screen()`
    - when calling `tmux.row()`
    - when the session is killed


A basic example of what you'll see

```
pytest --tmux-debug /tmp/test.py
================================================ test session starts =================================================
platform linux -- Python 3.7.16, pytest-7.2.1, pluggy-1.0.0
rootdir: /tmp
plugins: tmux-0.0.1, libtmux-0.20.0
collected 1 item

/tmp/test.py

pytest-tmux started with DEBUG

****************************************************************************************
* Open a new window terminal and use the bellow command to connect to the tmux session *
****************************************************************************************

tmux -S "/tmp/pytest-of-rockandska/pytest-1138/tmux.socket" attach -t "test_test_send_keys" \; setw force-width 80 \; setw force-height 24

Press enter to continue....

Check tmux screen
Press enter to continue....

Send "ls" to tmux session
Press enter to continue....

Check tmux screen
Press enter to continue....
.
Closing session
Press enter to continue....
                                                                                   [100%]

================================================= 1 passed in 37.08s =================================================
```
