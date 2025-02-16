from enum import Enum
from math import copysign
from typing import Any, Optional

import pandas as pd
from pandas import Timestamp

from pytrade.instruments import Instrument
from pytrade.interfaces.data import IInstrumentData


class TimeInForce(Enum):

    GOOD_TILL_CANCELLED = "GTC"
    GOOD_TILL_DATE = "GTD"
    GOOD_FOR_DAY = "GFD"
    FILL_OR_KILL = "FOK"
    PARTIAL_OR_KILL = "IOC"


class Order(dict):

    def __init__(
        self,
        instrument: Instrument,
        size: int,
        stop: Optional[float] = None,
        limit: Optional[float] = None,
        price_bound: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.GOOD_TILL_CANCELLED,
        take_profit_on_fill: Optional[float] = None,
        stop_loss_on_fill: Optional[float] = None,
        trailing_stop_loss_on_fill: Optional[float] = None,
        parent_trade: Optional["Trade"] = None,
    ):
        self._instrument: Instrument = instrument
        self._size: int = size
        self._stop = stop
        self._limit = limit
        self._price_bound = price_bound
        self._time_in_force: Optional[TimeInForce] = time_in_force
        self._take_profit_on_fill: Optional[float] = take_profit_on_fill
        self._stop_loss_on_fill: Optional[float] = stop_loss_on_fill
        self._trailing_stop_loss_on_fill: Optional[float] = trailing_stop_loss_on_fill
        self.__parent_trade = parent_trade

    def __str__(self):

        return (
            f"<Order instrument={self._instrument} size={self._size} "
            f"stop={self._stop} limit={self._limit} price_bound={self._price_bound}"
            f"time_in_force={self._time_in_force} tp={self.take_profit_on_fill} sl={self.stop_loss_on_fill}"
            f"trailing_sl={self._trailing_stop_loss_on_fill} parent_trade={self.__parent_trade}>"
        )

    def __eq__(self, other: Any):
        return other is self

    def __ne__(self, other: Any):
        return not self.__eq__(other)

    def resize(self, size):
        self._size = size

    @property
    def instrument(self) -> Instrument:
        return self._instrument

    @property
    def size(self) -> int:
        return self._size

    @property
    def time_in_force(self) -> TimeInForce:
        return (
            self._time_in_force
            if self._time_in_force
            else TimeInForce.GOOD_TILL_CANCELLED
        )

    @property
    def take_profit_on_fill(self) -> Optional[float]:
        return self._take_profit_on_fill

    @property
    def stop_loss_on_fill(self) -> Optional[float]:
        return self._stop_loss_on_fill

    @property
    def trailing_stop_loss_on_fill(self) -> Optional[float]:
        return self._trailing_stop_loss_on_fill

    @property
    def is_long(self):
        return self._size > 0

    @property
    def pricebound(self) -> Optional[float]:
        return self._price_bound

    @property
    def stop(self) -> Optional[float]:
        return self._stop

    @property
    def limit(self) -> Optional[float]:
        return self._limit

    @property
    def is_contingent(self) -> bool:
        return bool(self.__parent_trade)

    @property
    def parent_trade(self) -> Optional["Trade"]:
        return self.__parent_trade


class Trade:
    """
    When an `"Order"` is filled, it results in an active `Trade`.
    Find active trades in `Strategy.trades` and closed, settled trades in `Strategy.closed_trades`.
    """

    def __init__(
        self,
        instrument: Instrument,
        size: int,
        entry_price: float,
        entry_time: Timestamp,
        data: IInstrumentData,
        tag: Optional[str] = None,
    ):
        self.__instrument = instrument
        self.__size = size
        self.__entry_price = entry_price
        self.__data = data
        self.__exit_price: Optional[float] = None
        self.__entry_bar: int = data.df.index.get_loc(entry_time)  # type: ignore
        self.__exit_bar: Optional[int] = None
        self.__entry_time: Timestamp = entry_time
        self.__exit_time: Optional[Timestamp] = None
        self.__sl_order: Optional[Order] = None
        self.__tp_order: Optional[Order] = None
        self.__tag: Optional[str] = tag

    def __str__(self):  # pragma: no cover
        return (
            f'<Trade size={self.__size} time={self.__entry_time}-{self.__exit_time or ""} '
            f'price={self.__entry_price}-{self.__exit_price or ""} pl={self.pl:.0f}'
            f'{" tag=" + str(self.__tag) if self.__tag is not None else ""}>'
        )

    def reduce(self, size):
        self.__size = size

    def close(self, exit_price: float, exit_time: Timestamp):
        self.__exit_price = exit_price
        self.__exit_time = exit_time
        self.__exit_bar = self.__data.df.index.get_loc(exit_time)  # type: ignore

    # Fields getters
    @property
    def data(self):
        return self.__data

    @property
    def instrument(self):
        return self.__instrument

    @property
    def size(self):
        """Trade size (volume; negative for short trades)."""
        return self.__size

    @property
    def entry_price(self) -> float:
        """Trade entry price."""
        return self.__entry_price

    @property
    def exit_price(self) -> Optional[float]:
        """Trade exit price (or None if the trade is still active)."""
        return self.__exit_price

    @property
    def tag(self):
        """
        A tag value inherited from the `"Order"` that opened
        this trade.

        This can be used to track trades and apply conditional
        logic / subgroup analysis.

        See also `"Order".tag`.
        """
        return self.__tag

    # Extra properties

    @property
    def entry_time(self) -> pd.Timestamp:
        """Datetime of when the trade was entered."""
        return self.__entry_time

    @property
    def entry_bar(self) -> int:
        return self.__entry_bar

    @property
    def exit_time(self) -> Optional[pd.Timestamp]:
        """Datetime of when the trade was exited."""
        return self.__exit_time

    @property
    def exit_bar(self) -> Optional[int]:
        return self.__exit_bar

    @property
    def is_long(self):
        """True if the trade is long (trade size is positive)."""
        return self.__size > 0

    @property
    def is_short(self):
        """True if the trade is short (trade size is negative)."""
        return not self.is_long

    @property
    def pl(self):
        """Trade profit (positive) or loss (negative) in cash units."""
        price = self.__exit_price or self.__data.last_price
        return self.__size * (price - self.__entry_price)

    @property
    def pl_pct(self):
        """Trade profit (positive) or loss (negative) in percent."""
        price = self.__exit_price or self.__data.last_price
        return copysign(1, self.__size) * (price / self.__entry_price - 1) * 100

    @property
    def value(self):
        """Trade total value in cash (volume × price)."""
        price = self.__exit_price or self.__data.last_price
        return abs(self.__size) * price

    # SL/TP management API

    @property
    def sl(self) -> Optional[Order]:
        """
        Stop-loss price at which to close the trade.

        This variable is writable. By assigning it a new price value,
        you create or modify the existing SL order.
        By assigning it `None`, you cancel it.
        """
        return self.__sl_order

    @sl.setter
    def sl(self, order: Order):
        self.__sl_order = order

    @property
    def tp(self) -> Optional[Order]:
        """
        Take-profit price at which to close the trade.

        This property is writable. By assigning it a new price value,
        you create or modify the existing TP order.
        By assigning it `None`, you cancel it.
        """
        return self.__tp_order

    @tp.setter
    def tp(self, order: Order):
        self.__tp_order = order
