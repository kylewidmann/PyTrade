import asyncio
from abc import abstractmethod
from datetime import timedelta

from pandas import Timestamp
from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.data import IDataContext, IInstrumentData
from pytrade.models.instruments import (
    MINUTES_MAP,
    UPDATE_MAP,
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
        _max_granularity = None
        for subscription in self.subscriptions:
            if MINUTES_MAP[subscription.granularity] > max_interval:
                _max_granularity = subscription.granularity
            
            self._required_updates.append(subscription)


        if _max_granularity:
            self._update_frequency = UPDATE_MAP[_max_granularity]
        else:
            raise RuntimeError("Can not determine update frequency for strategy.")
        
        self._pending_updates = self._required_updates.copy()
        # Just set to min and let the first update set it correctly
        self._next_timestamp = Timestamp.min

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
            instrument_data.on_update += self._update_callback(instrument_data)

    def _update_callback(self, data: IInstrumentData):
        return lambda: self._handle_update(data)

    def _handle_update(self, data: IInstrumentData) -> None:
        # If data was missed move to the next update window based on data
        if data.timestamp > self._next_timestamp:
            self._next_timestamp = data.timestamp.ceil(freq=self._update_frequency)
            self._pending_updates = self._required_updates.copy()

        if data.timestamp == self._next_timestamp:
            self._pending_updates.remove(CandleSubscription(data.instrument, data.granularity))
        
        # Filter out update from pending
        if not self._pending_updates:
            self._updates_complete.set()
            self._next_timestamp + timedelta()

    def next(self) -> None:
        if self._updates_complete.is_set():
            self._updates_complete.clear()
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
