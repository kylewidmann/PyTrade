from copy import copy
from math import copysign
from typing import Optional, Union

import numpy as np
import pandas as pd

import pytrade.models.order as order


class Trade:
    """
    When an `"Order"` is filled, it results in an active `Trade`.
    Find active trades in `Strategy.trades` and closed, settled trades in `Strategy.closed_trades`.
    """

    def __init__(self, size: int, entry_price: float, entry_bar: int, tag):
        self.__size = size
        self.__entry_price = entry_price
        self.__exit_price: Optional[float] = None
        self.__entry_bar: int = entry_bar
        self.__exit_bar: Optional[int] = None
        self.__entry_time = None
        self.__exit_time = None
        self.__sl_order: Optional["order.Order"] = None
        self.__tp_order: Optional["order.Order"] = None
        self.__tag = tag

    def __repr__(self):
        return (
            f'<Trade size={self.__size} time={self.__entry_bar}-{self.__exit_bar or ""} '
            f'price={self.__entry_price}-{self.__exit_price or ""} pl={self.pl:.0f}'
            f'{" tag=" + str(self.__tag) if self.__tag is not None else ""}>'
        )

    def _replace(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, f"_{self.__class__.__qualname__}__{k}", v)
        return self

    def _copy(self, **kwargs):
        return copy(self)._replace(**kwargs)

    def close(self, portion: float = 1.0):
        """Place new `"Order"` to close `portion` of the trade at next market price."""
        if not 0 < portion <= 1:
            raise RuntimeError(
                f"Invalid portion for trade ({portion}).  Must be a fraction between 0 and 1."
            )

        size = copysign(max(1, round(abs(self.__size) * portion)), -self.__size)
        return order.Order(size, parent_trade=self, tag=self.__tag)

    # Fields getters

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
    def entry_bar(self) -> int:
        """Candlestick bar index of when the trade was entered."""
        return self.__entry_bar

    @property
    def exit_bar(self) -> Optional[int]:
        """
        Candlestick bar index of when the trade was exited
        (or None if the trade is still active).
        """
        return self.__exit_bar

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

    @property
    def _sl_order(self):
        return self.__sl_order

    @property
    def _tp_order(self):
        return self.__tp_order

    # Extra properties

    @property
    def entry_time(self) -> Union[pd.Timestamp, int]:
        """Datetime of when the trade was entered."""
        return self.__entry_time  # type: ignore

    @property
    def exit_time(self) -> Optional[Union[pd.Timestamp, int]]:
        """Datetime of when the trade was exited."""
        return self.__exit_time

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
        price = self.__exit_price
        return self.__size * (price - self.__entry_price)

    @property
    def pl_pct(self):
        """Trade profit (positive) or loss (negative) in percent."""
        price = self.__exit_price
        return copysign(1, self.__size) * (price / self.__entry_price - 1)

    @property
    def value(self):
        """Trade total value in cash (volume × price)."""
        price = self.__exit_price
        return abs(self.__size) * price

    # SL/TP management API

    @property
    def sl(self):
        """
        Stop-loss price at which to close the trade.

        This variable is writable. By assigning it a new price value,
        you create or modify the existing SL order.
        By assigning it `None`, you cancel it.
        """
        return self.__sl_order and self.__sl_order.stop

    @sl.setter
    def sl(self, price: float):
        self.__set_contingent("sl", price)

    @property
    def tp(self):
        """
        Take-profit price at which to close the trade.

        This property is writable. By assigning it a new price value,
        you create or modify the existing TP order.
        By assigning it `None`, you cancel it.
        """
        return self.__tp_order and self.__tp_order.limit

    @tp.setter
    def tp(self, price: float):
        self.__set_contingent("tp", price)

    def __set_contingent(self, type, price):
        if type not in ("sl", "tp"):
            raise RuntimeError(f"Invalid type supplied for trade {type}")

        if not (price is None or 0 < price < np.inf):
            raise RuntimeError(f"Invalid price ({price}) provided for trade.")

        attr = f"_{self.__class__.__qualname__}__{type}_order"
        order: "order.Order" = getattr(self, attr)
        if order:
            order.cancel()
        if price:
            kwargs = {"stop": price} if type == "sl" else {"limit": price}
            order = self.__broker.new_order(
                -self.size, trade=self, tag=self.tag, **kwargs
            )
            setattr(self, attr, order)
