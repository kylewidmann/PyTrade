import asyncio
from datetime import timedelta
from typing import Optional

import pandas as pd
from pandas import Timestamp

from pytrade.events.event import Event
from pytrade.instruments import Candlestick, Granularity, Instrument
from pytrade.interfaces.data import IDataContext, IInstrumentData

COLUMNS = ["datetime", "instrument", "open", "high", "low", "close"]

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
    def instrument(self):
        return self.__instrument

    @property
    def granularity(self):
        return self.__granularity

    @property
    def timestamp(self) -> Timestamp:
        return self._data.index[-1]

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


class CandleData(IDataContext):

    def __init__(self, max_size=1000):
        self._data: dict[tuple[Instrument, Granularity], InstrumentCandles] = {}
        self._max_size = max_size
        self._update_event = asyncio.Event()

    @property
    def universe(self) -> list[IInstrumentData]:
        return [v for k, v in self._data.items()]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        # Need to handle case where instantiatied and different max size is provided
        return cls.instance

    def get(self, instrument: Instrument, granularity: Granularity):
        key = (instrument, granularity)
        instrument_candles: InstrumentCandles = self._data.get(
            key, InstrumentCandles(max_size=self._max_size)
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
        self._update_event.set()

    async def next(self):
        await self._update_event.wait()
        self._update_event.clear()
