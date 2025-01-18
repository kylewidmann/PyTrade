import asyncio
from abc import abstractmethod

from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.data import IDataContext, IInstrumentData
from pytrade.models.instruments import (
    MINUTES_MAP,
    CandleSubscription,
    FxInstrument,
    Granularity,
    Instrument,
)
from pytrade.models.order import OrderRequest, TimeInForce


class FxStrategy:

    def __init__(self, broker: IBroker, data_context: IDataContext):
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
            instrument_data = self.broker.subscribe(
                subscription.instrument, subscription.granularity
            )
            instrument_data.on_update += lambda: self._handle_update(
                subscription.instrument, subscription.granularity
            )

    def _handle_update(self, instrument: Instrument, granularity: Granularity) -> None:
        self._pending_updates.remove(CandleSubscription(instrument, granularity))
        # Filter out update from pending
        if not self._pending_updates:
            self._updates_complete.set()

    async def next(self) -> None:
        await self._updates_complete.wait()
        self._next()
        self._pending_updates = self._required_updates.copy()

    def get_data(
        self, instrument: FxInstrument, granularity: Granularity
    ) -> IInstrumentData:
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

    def buy(
        self,
        instrument: Instrument,
        size,
        time_in_force: TimeInForce = TimeInForce.GOOD_TILL_CANCELLED,
        tp=None,
        sl=None,
    ) -> None:
        self.broker.order(OrderRequest(instrument, size, time_in_force, tp, sl))

    def sell(
        self,
        instrument: Instrument,
        size,
        time_in_force: TimeInForce = TimeInForce.GOOD_TILL_CANCELLED,
        tp=None,
        sl=None,
    ) -> None:
        self.buy(instrument, -size, time_in_force, tp, sl)
