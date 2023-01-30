from __future__ import annotations

from datetime import datetime
from functools import wraps
from time import sleep
from typing import Any, Callable, TypeVar, Union, cast

TRetry = TypeVar("TRetry", bound=Callable[..., bool])


class retry(object):
    def __init__(self, timeout: Union[int, float], delay: Union[int, float]) -> None:
        assert isinstance(timeout, (int, float))
        assert isinstance(delay, (int, float))
        self.timeout = timeout
        self.delay = delay

    def __call__(self, func: TRetry) -> TRetry:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> bool:
            start_time = datetime.now()
            while func(*args, **kwargs) is False:
                if (datetime.now() - start_time).total_seconds() <= self.timeout:
                    sleep(self.delay)
                else:
                    return False
            return True

        return cast(TRetry, wrapped)


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
        func: Callable[..., str],
        timeout: Union[int, float],
        delay: Union[int, float],
    ) -> None:
        self.func = func
        self.value = self.func()
        self.__timeout = timeout
        self.__delay = delay

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        @retry(timeout=self.__timeout, delay=self.__delay)
        def _test() -> bool:
            self.value = self.func()
            return self.value == other

        return _test()

    def __ne__(self, other: object) -> bool:
        @retry(timeout=self.__timeout, delay=self.__delay)
        def _test() -> bool:
            self.value = self.func()
            return not self.value == other

        return _test()

    def __contains__(self, other: str) -> bool:
        @retry(timeout=self.__timeout, delay=self.__delay)
        def _test() -> bool:
            self.value = self.func()
            return other in self.value

        return _test()
