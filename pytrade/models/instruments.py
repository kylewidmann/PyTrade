from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import pandas as pd
import pytz
from pandas import Timestamp

from pytrade.events.event import Event
from pytrade.interfaces.data import IInstrumentData


class Granularity(Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"


MINUTES_MAP = {
    Granularity.M1: 1,
    Granularity.M5: 5,
    Granularity.M15: 15,
    Granularity.H1: 60,
    Granularity.H4: 240,
}


class Instrument(Enum):
    AUDJPY = "AUD/JPY"
    AUDNZD = "AUD/NZD"
    AUDUSD = "AUD/USD"
    CADJPY = "CAD/JPY"
    CHFJPY = "CHF/JPY"
    EURCHF = "EUR/CHF"
    EURGBP = "EUR/GBP"
    EURJPY = "EUR/JPY"
    EURPLN = "EUR/PLN"
    EURUSD = "EUR/USD"
    GBPJPY = "GBP/JPY"
    GBPUSD = "GBP/USD"
    NZDUSD = "NZD/USD"
    USDCAD = "USD/CAD"
    USDCHF = "USD/CHF"
    USDJPY = "USD/JPY"
    USDMXN = "USD/MXN"
    USDRUB = "USD/RUB"
    USDTRY = "USD/TRY"
    USDZAR = "USD/ZAR"


instrument_lookup = {m.value: m for m in Instrument}


class CandleSubscription:

    def __init__(self, instrument: Instrument, granularity: Granularity):
        self._instrument = instrument
        self._granularity = granularity

    @property
    def granularity(self) -> Granularity:
        return self._granularity

    @property
    def instrument(self) -> Instrument:
        return self._instrument

    def __hash__(self):
        return hash((self.instrument, self.granularity))

    def __gt__(self, other):
        return (
            isinstance(other, CandleSubscription)
            and self.instrument.value < other.instrument.value
            and self.granularity.value > other.granularity.value
        )

    def __lt__(self, other):
        return (
            isinstance(other, CandleSubscription)
            and self.instrument.value > other.instrument.value
            and self.granularity.value < other.granularity.value
        )

    def __eq__(self, other):
        return (
            isinstance(other, CandleSubscription)
            and self.instrument.value == other.instrument.value
            and self.granularity.value == other.granularity.value
        )


class Candlestick:

    def __init__(
        self,
        instrument: Instrument,
        granularity: Granularity,
        open: float,
        high: float,
        low: float,
        close: float,
        timestamp: Timestamp,
    ):
        self.instrument = instrument
        self.granularity = granularity
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "Timestamp": self.timestamp,
            "Instrument": self.instrument,
            "Open": self.open,
            "High": self.open,
            "Low": self.open,
            "Close": self.open,
        }


class TickData:

    instrument: Instrument
    timestamp: datetime
    bid: float
    ask: float

    def __init__(self, instrument: str, timestamp: str, bid: str, ask: str):
        self.instrument = instrument_lookup[instrument]
        tz = pytz.timezone("UTC")
        self.timestamp = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S.%f").astimezone(
            tz
        )
        self.bid = float(bid)
        self.ask = float(ask)


COLUMNS = ["Timestamp", "Instrument", "Open", "High", "Low", "Close"]

INDEX = COLUMNS[0]


class InstrumentCandles(IInstrumentData):

    def __init__(
        self, data: Optional[pd.DataFrame] = None, max_size: Optional[int] = None
    ):
        self._data: pd.DataFrame = (
            data if data is not None else pd.DataFrame(columns=COLUMNS)
        )
        if not isinstance(self._data.index, pd.DatetimeIndex):
            if INDEX in self._data.columns:
                self._data.set_index([INDEX], inplace=True)
            else:
                raise RuntimeError(
                    "Dataframe does not have a datetime index and does not have a 'Timestamp' column"
                )
        self._max_size: Optional[int] = max_size
        self.__instrument: Optional[Instrument] = None
        self.__granularity: Optional[Granularity] = None
        self.__update_event = Event()

    @property
    def df(self):
        return self._data

    @property
    def on_update(self):
        return self.__update_event

    @on_update.setter
    def on_update(self, value: Event):
        self.__update_event = value

    def update(self, candlestick: Candlestick):
        if not self.__instrument:
            self.__instrument = candlestick.instrument
            self.__granularity = candlestick.granularity

        if candlestick.instrument != self.__instrument:
            raise RuntimeError(
                f"Received {candlestick.instrument} for history[{self.__instrument}]"
            )

        if candlestick.granularity != self.__granularity:
            raise RuntimeError(
                f"Received {candlestick.granularity} for history[{self.__granularity}]"
            )

        if self._max_size and len(self._data) >= self._max_size:
            _delta = self._data.index[-1] - self._data.index[-2]
            if not isinstance(_delta, timedelta):
                raise RuntimeError(
                    "Expected dataframe to have DatetimeInex. Unable to caluclate timedelta from index."
                )
            self._data.index = self._data.index.shift(  # type: ignore
                int(_delta.seconds / 60), freq="min"
            )
            self._data = self._data.shift(-1)

        self._data.loc[candlestick.timestamp] = [  # type: ignore
            candlestick.instrument,
            candlestick.open,
            candlestick.high,
            candlestick.low,
            candlestick.close,
        ]
        self.__update_event()


class CandleData:

    def __init__(self, max_size=1000):
        self._data: dict[tuple[Instrument, Granularity], InstrumentCandles] = {}
        self._max_size = max_size

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        # Need to handle case where instantiatied and different max size is provided
        return cls.instance

    def get(self, instrument: Instrument, granularity: Granularity):
        key = (instrument, granularity)
        instrument_candles: InstrumentCandles = self._data.get(
            (instrument, granularity), InstrumentCandles(max_size=self._max_size)
        )
        self._data[key] = instrument_candles
        return instrument_candles

    def update(self, candle: Candlestick):
        key = (candle.instrument, candle.granularity)
        instrument_candles: InstrumentCandles = self._data.get(
            key,
            InstrumentCandles(max_size=self._max_size),
        )
        self._data[key] = instrument_candles
        instrument_candles.update(candle)
