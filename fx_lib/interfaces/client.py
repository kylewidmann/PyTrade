import abc
from typing import Callable

from fx_lib.models.instruments import Candlestick, Granularity, Instrument
from fx_lib.models.order import OrderRequest


class IClient(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "subscribe")
            and callable(subclass.subscribe)
            or NotImplemented
        )

    @abc.abstractmethod
    def new_order(self, order: OrderRequest):
        raise NotImplementedError

    @abc.abstractmethod
    def subscribe(
        self,
        instrument: Instrument,
        granularity: Granularity,
        callback: Callable[[Candlestick], None],
    ):
        raise NotImplementedError()
