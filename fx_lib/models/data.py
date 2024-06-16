

from datetime import datetime
from dateutil import parser
from fx_lib.models.instruments import Instrument

import pytz

pair_map = {m.value: m for m in Instrument}

class Candlestick:

    symbol: Instrument
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float

    def __init__(self, symbol, open, high, low, close, timestamp):
        self.symbol = symbol
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.timestamp = timestamp

class TickData:

    symbol: Instrument
    timestamp: datetime
    bid: float
    ask: float

    def __init__(self, symbol, timestamp, bid, ask):
        self.symbol = pair_map[symbol]
        tz = pytz.timezone('UTC')
        self.timestamp = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S.%f").astimezone(tz)
        # self.timestamp = self.timestamp.astimezone(tz)
        # self.timestamp = parser.parse(timestamp, tzinfo=)
        self.bid = float(bid)
        self.ask = float(ask)

class Trade:

    def __init__(self):
        pass