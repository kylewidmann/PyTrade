import asyncio
from abc import abstractmethod

from pytrade.interfaces.broker import IBroker
from pytrade.models.indicator import Indicator
from pytrade.models.instruments import (
    MINUTES_MAP,
    CandleData,
    Candlestick,
    CandleSubscription,
    Granularity,
    Instrument,
    InstrumentCandles,
)


class FxStrategy:

    def __init__(self, broker: IBroker, data_context: CandleData):
        self.broker = broker
        self._updates_complete = asyncio.Event()
        self._data_context = data_context
        self._pending_updates: list[CandleSubscription] = []

    def init(self) -> None:
        self._caluclate_updates()
        self._monitor_instruments()
        self._init()

    def _caluclate_updates(self) -> None:
        self._required_updates: list[CandleSubscription] = []
        max_interval = 0
        for subscription in self.subscriptions:
            max_interval = max(max_interval, MINUTES_MAP[subscription.granularity])

        for subscription in self.subscriptions:
            expected_update_count = int(
                max_interval / MINUTES_MAP[subscription.granularity]
            )
            self._required_updates += [
                subscription for _ in range(expected_update_count)
            ]

        self._pending_updates = self._required_updates.copy()

    @property
    @abstractmethod
    def subscriptions(self) -> list[CandleSubscription]:
        """
        Declare the `InstrumentSubscription`s this strategy should use
        for its signals
        """
        raise NotImplementedError()

    def _monitor_instruments(self) -> None:
        for subscription in self.subscriptions:
            self.broker.subscribe(
                subscription.instrument,
                subscription.granularity,
                self._update_instrument,
            )

    def _update_instrument(self, candle: Candlestick) -> None:
        self._data_context.update(candle)
        self._pending_updates.remove(
            CandleSubscription(candle.instrument, candle.granularity)
        )
        # Filter out update from pending
        if not self._pending_updates:
            self._updates_complete.set()

    async def next(self) -> None:
        await self._updates_complete.wait()
        self._next()
        self._pending_updates = self._required_updates.copy()

    def get_data(
        self, instrument: Instrument, granularity: Granularity
    ) -> InstrumentCandles:
        return self._data_context.get(instrument, granularity)

    @abstractmethod
    def _init(self) -> None:
        """
        Create indicators to be used for signals in the `_next` method.
        """
        raise NotImplementedError()

    @abstractmethod
    def _next(self) -> None:
        """
        Evaluate indicators and submit orders to the broker
        """
        raise NotImplementedError()

    def buy(self, size, tp=None, sl=None) -> None:
        pass

    def sell(self, size, tp=None, sl=None) -> None:
        pass


class BacktestStrategy:

    def init(self):
        self._create_indicators()
        self._register_indicators()

    def _create_indicators(self):
        pass

    def _register_indicators(self):
        self._indicators = {
            attr: indicator
            for attr, indicator in self.__dict__.items()
            if isinstance(indicator, Indicator)
        }.items()

    def next(self):
        for attr, indicator in self._indicator_attrs:
            # Slice indicator on the last dimension (case of 2d indicator)
            setattr(self, attr, indicator[..., : len(self.data)])


# class StrategyWrapper:

#     def __init__(self, broker, data, params):
#         self._klass: Type[Strategy] = params.get("_klass")
#         super().__init__(broker, data, params)

#     def init(self):
#         self._strategy = self._klass(self._broker, self.data)
#         self._strategy.init()
#         # Pre calculate indicators
#         self._indicators = {
#             attr: indicator
#             for attr, indicator in self._strategy.__dict__.items()
#             if isinstance(indicator, Indicator)
#         }.items()

#     def next(self):
#         for attr, indicator in self._indicators:
#             # Slice indicator on the last dimension (case of 2d indicator)
#             setattr(self._strategy, attr, indicator[..., : len(self.data)])
#         self._strategy.next()


class BacktestBroker(IBroker):

    pass
