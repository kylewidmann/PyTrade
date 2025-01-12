import abc
from typing import Callable

from multimethod import multimethod

from pytrade.models.instruments import Candlestick, Granularity, FxInstrument
from pytrade.models.order import MarketOrderRequest


class IClient:

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "order")
            and callable(subclass.order)
            and hasattr(subclass, "get_candles")
            and callable(subclass.get_candles)
            and hasattr(subclass, "get_candle")
            and callable(subclass.get_candle)
            and hasattr(subclass, "subscribe")
            and callable(subclass.subscribe)
        ) or NotImplemented

    @abc.abstractmethod
    @multimethod
    def order(self, order: MarketOrderRequest):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_candles(
        self, instrument: FxInstrument, granularity: Granularity, count: int
    ) -> list[Candlestick]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_candle(
        self, instrument: FxInstrument, granularity: Granularity
    ) -> Candlestick:
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe(
        self,
        instrument: FxInstrument,
        granularity: Granularity,
        callback: Callable[[Candlestick], None],
    ):
        raise NotImplementedError()
