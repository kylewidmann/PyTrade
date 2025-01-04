import asyncio
from abc import abstractmethod

from pytrade.interfaces.broker import IBroker
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
