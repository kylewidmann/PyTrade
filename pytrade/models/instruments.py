from datetime import datetime
from enum import Enum
from typing import Any, Union

import pytz
from pandas import Timestamp

Instrument = Union["FxInstrument", str]


class Granularity(Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"


MINUTES_MAP = {
    Granularity.M1: 1,
    Granularity.M5: 5,
    Granularity.M15: 15,
    Granularity.H1: 60,
    Granularity.H4: 240,
    Granularity.D1: 1440,
}

UPDATE_MAP = {
    Granularity.M1: "1min",
    Granularity.M5: "5min",
    Granularity.M15: "15min",
    Granularity.H1: "1h",
    Granularity.H4: "4h",
    Granularity.D1: "24h",
}

class FxInstrument(Enum):
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


instrument_lookup = {m.value: m for m in FxInstrument}


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

    def __eq__(self, other: "CandleSubscription"):
        result =  (
            isinstance(other, CandleSubscription)
            and self.__instrument_eq__(other)
        )

        return result
    
    def __instrument_eq__(self, other: "CandleSubscription"):
        result = (
            (
                isinstance(other.instrument, FxInstrument)
                and isinstance(self.instrument, FxInstrument)
                and self.instrument.value == other.instrument.value
            ) or (
                isinstance(other.instrument, str)
                and isinstance(self.instrument, str)
                and self.instrument == other.instrument
            )
        )

        return result


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
