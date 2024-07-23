import abc
from typing import Callable

from fx_lib.models.instruments import Candlestick, Granularity, Instrument
from fx_lib.models.order import OrderRequest


class IBroker(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "order")
            and callable(subclass.order)
            and hasattr(subclass, "equity")
            and hasattr(subclass, "margin_available")
            or NotImplemented
        )

    @property
    @abc.abstractmethod
    def equity(self) -> float:
        raise NotImplementedError()
        return self._cash + sum(trade.pl for trade in self.trades)

    @property
    @abc.abstractmethod
    def margin_available(self) -> float:
        raise NotImplementedError()
        # From https://github.com/QuantConnect/Lean/pull/3768
        margin_used = sum(trade.value / self._leverage for trade in self.trades)
        return max(0, self.equity - margin_used)

    @abc.abstractmethod
    def order(self, order: OrderRequest):
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe(
        self,
        instrument: Instrument,
        granularity: Granularity,
        callback: Callable[[Candlestick], None],
    ):
        raise NotImplementedError()
