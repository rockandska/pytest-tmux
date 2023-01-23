from datetime import datetime
from time import sleep


def retry(func=None, *, timeout=None, delay=None):
    def _decorate(function):
        def wrapped_function(*args, **kwargs):
            start_time = datetime.now()
            if not isinstance(timeout, (int, float)):
                raise ValueError(
                    "timeout: expecting int/float but was {}".format(
                        type(timeout).__name__
                    )
                )
            if not isinstance(delay, (int, float)):
                raise ValueError(
                    "delay: expecting int/float but was {}".format(type(delay).__name__)
                )
            while function(*args, **kwargs) is False:
                if (datetime.now() - start_time).total_seconds() <= timeout:
                    sleep(delay)
                else:
                    return False
            return True

        return wrapped_function

    if func:
        return _decorate(func)
    return _decorate


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
