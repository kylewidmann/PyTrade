from enum import Enum
from typing import Optional

from fx_lib.models.instruments import Instrument


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


class OrderRequest(dict):

    def __init__(
        self,
        instrument: Instrument,
        units: int,
        time_in_force: TimeInForce,
        take_profit_on_fill: Optional[float],
        stop_loss_on_fill: Optional[float],
        trailing_stop_loss_on_fill: Optional[float],
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
