from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class TypedEvent(Generic[T]):

    def __init__(self):
        self.__callbacks: list[Callable[[T], None]] = []

    @property
    def _callbacks(self):
        return self.__callbacks

    def __iadd__(self, callback: Callable[[T], None]):
        self.__callbacks.append(callback)
        return self

    def __isub__(self, callback: Callable[[T], None]):
        self.__callbacks.remove(callback)
        return self

    def __call__(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)


class Event:

    def __init__(self):
        self.__callbacks: list[Callable[[], None]] = []

    @property
    def _callbacks(self):
        return self.__callbacks

    def __iadd__(self, callback: Callable[[], None]):
        self.__callbacks.append(callback)
        return self

    def __isub__(self, callback: Callable[[], None]):
        self.__callbacks.remove(callback)
        return self

    def __call__(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)
