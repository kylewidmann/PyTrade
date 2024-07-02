from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import pandas as pd
import pytz

InstrumentSubscription = namedtuple('InstrumentSubscription', ['instrument', 'granularity'])

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

class Candlestick:

    instrument: Instrument
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float

    def __init__(self, instrument, open, high, low, close, timestamp):
        self.instrument = instrument
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.timestamp = timestamp

class TickData:

    instrument: Instrument
    timestamp: datetime
    bid: float
    ask: float

    def __init__(self, instrument: str, timestamp: str, bid: str, ask: str):
        self.instrument = instrument_lookup[instrument]
        tz = pytz.timezone('UTC')
        self.timestamp = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S.%f").astimezone(tz)
        self.bid = float(bid)
        self.ask = float(ask)

COLUMNS = [
    'Timestamp',
    'Instrument',
    'Open',
    'High',
    'Low',
    'Close'
]

class InstrumentHistory:

    def __init__(self, data: Optional[pd.DataFrame] = None, max_history: Optional[int] = None):
        self._data: pd.DataFrame = data if data else pd.DataFrame(columns=COLUMNS)
        self._data.set_index(COLUMNS[0], inplace=True)
        self._max_history: Optional[int] = max_history

    @property
    def df(self):
        return self._data

    def update(self, candlestick: Candlestick):
        if self._max_history and len(self._data) >= self._max_history:
            _delta = (self._data.index[-1] - self._data.index[-2])
            if not isinstance(_delta, timedelta):
                raise RuntimeError("Expected dataframe to have DatetimeInex. Unable to caluclate timedelta from index.")
            self._data.index = self._data.index.shift(_delta.seconds / 60, freq="min")
            self._data = self._data.shift(-1)

        self._data.loc[candlestick.timestamp] = [
            candlestick.instrument,
            candlestick.open,
            candlestick.high,
            candlestick.low,
            candlestick.close,
        ]