from datetime import datetime
from time import sleep
from functools import wraps


class retry(object):
    def __init__(self, timeout=None, delay=None):
        assert isinstance(timeout, (int, float))
        assert isinstance(delay, (int, float))
        self.timeout = timeout
        self.delay = delay

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            start_time = datetime.now()
            while func(*args, **kwargs) is False:
                if (datetime.now() - start_time).total_seconds() <= self.timeout:
                    sleep(self.delay)
                else:
                    return False
            return True
        return wrapped


class TmuxOutput(object):
    """
    Sucharge some operator to add @retry property

    Args:
        func: function used to get the value to use when required
        timeout: how long to wait for the operator call to fail
        delay: how long before retrying the operator call

    Returns:
        a [TmuxOutput][pytest_tmux.output.TmuxOutput] instance
    """

    def __init__(
        self,
        func,
        timeout=None,
        delay=None,
    ):
        self.func = func
        self.value = self.func()
        self.__timeout = timeout
        self.__delay = delay

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        @retry(timeout=self.__timeout, delay=self.__delay)
        def _test():
            self.value = self.func()
            return self.value == other

        return _test()

    def __ne__(self, other):
        @retry(timeout=self.__timeout, delay=self.__delay)
        def _test():
            self.value = self.func()
            return not self.value == other

        return _test()

    def __contains__(self, other):
        @retry(timeout=self.__timeout, delay=self.__delay)
        def _test():
            self.value = self.func()
            return other in self.value

        return _test()
