from enum import Enum
from typing import Optional

from pytrade.models.instruments import Instrument
from pytrade.models.trade import Trade


class TimeInForce(Enum):

    GOOD_TILL_CANCELLED = "GTC"
    GOOD_TILL_DATE = "GTD"
    GOOD_FOR_DAY = "GFD"
    FILL_OR_KILL = "FOK"
    PARTIAL_OR_KILL = "IOC"


class OrderType(Enum):

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class Order:
    """
    Place new orders through `Strategy.buy()` and `Strategy.sell()`.
    Query existing orders through `Strategy.orders`.

    When an order is executed or [filled], it results in a `Trade`.

    If you wish to modify aspects of a placed but not yet filled order,
    cancel it and place a new one instead.

    All placed orders are [Good 'Til Canceled].

    [filled]: https://www.investopedia.com/terms/f/fill.asp
    [Good 'Til Canceled]: https://www.investopedia.com/terms/g/gtc.asp
    """

    def __init__(
        self,
        size: float,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        parent_trade: Optional["Trade"] = None,
        tag: object = None,
    ):
        if size == 0:
            raise RuntimeError("Invalid size provided for order.")

        self.__size = size
        self.__limit_price = limit_price
        self.__stop_price = stop_price
        self.__sl_price = sl_price
        self.__tp_price = tp_price
        self.__parent_trade = parent_trade
        self.__tag = tag

    def _replace(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, f"_{self.__class__.__qualname__}__{k}", v)
        return self

    def __repr__(self):
        return "<Order {}>".format(
            ", ".join(
                f"{param}={round(value, 5)}"
                for param, value in (
                    ("size", self.__size),
                    ("limit", self.__limit_price),
                    ("stop", self.__stop_price),
                    ("sl", self.__sl_price),
                    ("tp", self.__tp_price),
                    ("contingent", self.is_contingent),
                    ("tag", self.__tag),
                )
                if value is not None
            )
        )

    # Fields getters

    @property
    def size(self) -> float:
        """
        Order size (negative for short orders).

        If size is a value between 0 and 1, it is interpreted as a fraction of current
        available liquidity (cash plus `Position.pl` minus used margin).
        A value greater than or equal to 1 indicates an absolute number of units.
        """
        return self.__size

    @property
    def limit(self) -> Optional[float]:
        """
        Order limit price for [limit orders], or None for [market orders],
        which are filled at next available price.

        [limit orders]: https://www.investopedia.com/terms/l/limitorder.asp
        [market orders]: https://www.investopedia.com/terms/m/marketorder.asp
        """
        return self.__limit_price

    @property
    def stop(self) -> Optional[float]:
        """
        Order stop price for [stop-limit/stop-market][_] order,
        otherwise None if no stop was set, or the stop price has already been hit.

        [_]: https://www.investopedia.com/terms/s/stoporder.asp
        """
        return self.__stop_price

    @property
    def sl(self) -> Optional[float]:
        """
        A stop-loss price at which, if set, a new contingent stop-market order
        will be placed upon the `Trade` following this order's execution.
        See also `Trade.sl`.
        """
        return self.__sl_price

    @property
    def tp(self) -> Optional[float]:
        """
        A take-profit price at which, if set, a new contingent limit order
        will be placed upon the `Trade` following this order's execution.
        See also `Trade.tp`.
        """
        return self.__tp_price

    @property
    def parent_trade(self):
        return self.__parent_trade

    @property
    def tag(self):
        """
        Arbitrary value (such as a string) which, if set, enables tracking
        of this order and the associated `Trade` (see `Trade.tag`).
        """
        return self.__tag

    # Extra properties

    @property
    def is_long(self):
        """True if the order is long (order size is positive)."""
        return self.__size > 0

    @property
    def is_short(self):
        """True if the order is short (order size is negative)."""
        return self.__size < 0

    @property
    def is_contingent(self):
        """
        True for [contingent] orders, i.e. [OCO] stop-loss and take-profit bracket orders
        placed upon an active trade. Remaining contingent orders are canceled when
        their parent `Trade` is closed.

        You can modify contingent orders through `Trade.sl` and `Trade.tp`.

        [contingent]: https://www.investopedia.com/terms/c/contingentorder.asp
        [OCO]: https://www.investopedia.com/terms/o/oco.asp
        """
        return bool(self.__parent_trade)

    def cancel(self):
        trade = self.__parent_trade
        if trade:
            if self is trade._sl_order:
                trade._replace(sl_order=None)
            elif self is trade._tp_order:
                trade._replace(tp_order=None)
            else:
                raise RuntimeError()


class OrderRequest(dict):

    def __init__(
        self,
        instrument: Instrument,
        units: int,
        time_in_force: TimeInForce,
        take_profit_on_fill: Optional[float] = None,
        stop_loss_on_fill: Optional[float] = None,
        trailing_stop_loss_on_fill: Optional[float] = None,
    ):
        # super().__init__(
        #     instrument=instrument,
        #     units=units,
        #     price=price,
        #     time_in_force=time_in_force,
        #     take_profit_on_fill=take_profit_on_fill,
        #     stop_loss_on_fill=stop_loss_on_fill,
        #     trailing_stop_loss_on_fill=trailing_stop_loss_on_fill
        # )
        self._instrument: Instrument = instrument
        self._units: int = units
        self._time_in_force: Optional[TimeInForce] = time_in_force
        self._take_profit_on_fill: Optional[float] = take_profit_on_fill
        self._stop_loss_on_fill: Optional[float] = stop_loss_on_fill
        self._trailing_stop_loss_on_fill: Optional[float] = trailing_stop_loss_on_fill

    @property
    def instrument(self) -> Instrument:
        return self._instrument

    @property
    def units(self) -> int:
        return self._units

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


class MarketOrderRequest(OrderRequest):

    def __init__(
        self,
        instrument: Instrument,
        units: int,
        time_in_force: TimeInForce = TimeInForce.FILL_OR_KILL,
        take_profit_on_fill: Optional[float] = None,
        stop_loss_on_fill: Optional[float] = None,
        trailing_stop_loss_on_fill: Optional[float] = None,
        price_bound: Optional[float] = None,
    ):
        super().__init__(
            instrument,
            units,
            time_in_force,
            take_profit_on_fill,
            stop_loss_on_fill,
            trailing_stop_loss_on_fill,
        )
        self._price_bound = price_bound

    @property
    def type(self):
        return OrderType.MARKET

    @property
    def pricebound(self) -> Optional[float]:
        return self._price_bound


class LimitOrderRequest(OrderRequest):

    def __init__(
        self,
        instrument: Instrument,
        units: int,
        price: float,
        time_in_force: TimeInForce,
        take_profit_on_fill: Optional[float],
        stop_loss_on_fill: Optional[float],
        trailing_stop_loss_on_fill: Optional[float],
    ):
        self._price = price

    @property
    def type(self):
        return OrderType.LIMIT

    @property
    def price(self) -> float:
        return self._price


class StopOrderRequest(OrderRequest):

    def __init__(
        self,
        instrument: Instrument,
        units: int,
        price: float,
        time_in_force: TimeInForce,
        position_fill: float,
        take_profit_on_fill: float,
        stop_loss_on_fill: float,
        trailing_stop_loss_on_fill: float,
        price_bound: Optional[float],
    ):
        self._price = price
        self._price_bound = price_bound

    @property
    def type(self):
        return OrderType.STOP

    @property
    def price(self) -> float:
        return self._price

    @property
    def pricebound(self) -> Optional[float]:
        return self._price_bound
