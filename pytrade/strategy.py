import asyncio
from abc import abstractmethod
from datetime import timedelta, timezone
from typing import Optional

from pandas import Timestamp

from pytrade.instruments import (
    MINUTES_MAP,
    UPDATE_MAP,
    CandleSubscription,
    Granularity,
    Instrument,
)
from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.data import IDataContext, IInstrumentData
from pytrade.logging import get_logger
from pytrade.models import Order, TimeInForce


class FxStrategy:

    def __init__(self, broker: IBroker, data_context: IDataContext):
        self.broker = broker
        self._updates_complete = asyncio.Event()
        self._data_context = data_context
        self._pending_updates: list[CandleSubscription] = []
        self.logger = get_logger()

    def init(self) -> None:
        self.logger.info("Initializing strategy.")
        self._caluclate_updates()
        # Call init first incase any indicators preload data for initial signals
        self._init()
        self._monitor_instruments()

    def _caluclate_updates(self) -> None:
        self.logger.debug("Calculating update intervals.")
        self._required_updates: list[CandleSubscription] = []
        max_interval = 0
        _max_granularity = None
        for subscription in self.subscriptions:
            if MINUTES_MAP[subscription.granularity] > max_interval:
                _max_granularity = subscription.granularity

            self._required_updates.append(subscription)

        if _max_granularity:
            self._update_frequency = UPDATE_MAP[_max_granularity]
            self._update_minutes = MINUTES_MAP[_max_granularity]
        else:
            raise RuntimeError("Can not determine update frequency for strategy.")

        self._pending_updates = self._required_updates.copy()
        # Just set to min and let the first update set it correctly
        self._next_timestamp = Timestamp.min.replace(tzinfo=timezone.utc)

        self.logger.debug(
            f"Set updates to [{str.join(" ", (str(update) for update in self._required_updates))}] \
and next update time to {self._next_timestamp}"
        )

    @property
    @abstractmethod
    def subscriptions(self) -> list[CandleSubscription]:
        """
        Declare the `InstrumentSubscription`s this strategy should use
        for its signals
        """
        raise NotImplementedError()

    def _monitor_instruments(self) -> None:
        self.logger.debug("Subscribing to instruments.")
        for subscription in self.subscriptions:
            instrument_data = self.broker.subscribe(
                subscription.instrument, subscription.granularity
            )
            instrument_data.on_update += self._update_callback(instrument_data)
            self.logger.debug(f"Subscribed to {subscription}.")
        self.logger.debug("Subscriptions complete")

    def _update_callback(self, data: IInstrumentData):
        return lambda: self._handle_update(data)

    def _handle_update(self, data: IInstrumentData) -> None:
        self.logger.debug(f"Received upate for {data}")
        # If data was missed move to the next update window based on data
        if data.timestamp > self._next_timestamp:
            self.logger.debug(
                f"Received an update for {data} that is past the expected update time {self._next_timestamp}."
            )
            self._next_timestamp = data.timestamp.ceil(freq=self._update_frequency)
            self._pending_updates = self._required_updates.copy()
            self.logger.debug(F"Updated next update time to {self._next_timestamp} and reset pending updates.")

        if data.timestamp == self._next_timestamp:
            self.logger.debug(f"Removing update for {data}.")
            self._pending_updates.remove(
                CandleSubscription(data.instrument, data.granularity)
            )

        # Filter out update from pending
        if not self._pending_updates:
            self.logger.debug(f"Updates for {self} compelete.")
            self._updates_complete.set()
            self._next_timestamp + timedelta(minutes=self._update_minutes)
            self.logger.debug(f"Updated next timestamp to {self._next_timestamp}.")

        self.logger.debug(f"Done handling upate for {data}.")

    def next(self) -> None:
        if self._updates_complete.is_set():
            self.logger.debug(f"Update complete. Running indicators.")
            self._updates_complete.clear()
            self._next()
            self._pending_updates = self._required_updates.copy()
            self.logger.debug(f"Strategy iteration complete. Reset updates.")

    def get_data(
        self, instrument: Instrument, granularity: Granularity
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
        stop: Optional[float] = None,
        limit: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GOOD_TILL_CANCELLED,
        tp=None,
        sl=None,
    ) -> None:
        order = Order(
                instrument,
                size,
                stop,
                limit,
                time_in_force=time_in_force,
                take_profit_on_fill=tp,
                stop_loss_on_fill=sl,
            )
        self.logger.info(f"Placing order {order}")
        self.broker.order(order)

    def sell(
        self,
        instrument: Instrument,
        size,
        stop: Optional[float] = None,
        limit: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GOOD_TILL_CANCELLED,
        tp=None,
        sl=None,
    ) -> None:
        self.buy(instrument, -size, stop, limit, time_in_force, tp, sl)
