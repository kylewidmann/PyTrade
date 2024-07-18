import random
from datetime import datetime, timedelta

import pandas as pd

from fx_lib.models.data import Indicator
from fx_lib.models.instruments import (
    MINUTES_MAP,
    Candlestick,
    Granularity,
    Instrument,
    InstrumentCandles,
)


def get_candles(
    count: int, instrument: Instrument, granularity: Granularity, end_time: datetime
) -> list[Candlestick]:
    _delta = MINUTES_MAP[granularity]
    return [
        Candlestick(
            instrument,
            granularity,
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            end_time - timedelta(minutes=_delta * i),
        )
        for i in range(count)
    ]


class BoolIndicator(Indicator):

    def _run(self):
        return self._data.Open.astype(bool)


class SquareIndicator(Indicator):

    def _run(self):
        return self._data.Open**2


class StaticIndicator(Indicator):

    def _run(self):
        return self._data.Open


class AddIndicator(Indicator):

    def _run(self):
        return self._data.Open + 1


class SubtractIndicator(Indicator):

    def _run(self):
        return self._data.Open - 1


def test_update():
    test_series = pd.Series([0, 1, 0, 0, 1])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = BoolIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert bool(indicator) == bool(value)

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1]


def test_primitive_equality():
    test_series = pd.Series([0, 1, 2, 3, 4])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = SquareIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert indicator == value**2

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1] ** 2


def test_primitive_greater():
    test_series = pd.Series([0, 1, 2, 3, 4])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = StaticIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert indicator > value - 1

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1]


def test_primitive_less():
    test_series = pd.Series([0, 1, 2, 3, 4])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = StaticIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert indicator < value + 1

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1]


def test_indicator_equality():
    test_series = pd.Series([0, 1, 2, 3, 4])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = StaticIndicator(data)
    indicator2 = StaticIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert indicator == indicator2

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1]
    assert len(indicator2._values) == len(test_series)
    assert indicator2.value == test_series.iloc[-1]


def test_indicator_greater():
    test_series = pd.Series([0, 1, 2, 3, 4])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = StaticIndicator(data)
    indicator2 = SubtractIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert indicator > indicator2

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1]
    assert len(indicator2._values) == len(test_series)
    assert indicator2.value == test_series.iloc[-1] - 1


def test_indicator_less():
    test_series = pd.Series([0, 1, 2, 3, 4])
    data = InstrumentCandles()
    candles = get_candles(
        len(test_series), Instrument.EURUSD, Granularity.M1, datetime.now()
    )
    indicator = StaticIndicator(data)
    indicator2 = AddIndicator(data)
    for idx, candle in enumerate(candles):
        value = test_series[idx]
        candle.open = value
        data.update(candle)
        assert indicator < indicator2

    assert len(indicator._values) == len(test_series)
    assert indicator.value == test_series.iloc[-1]
    assert len(indicator2._values) == len(test_series)
    assert indicator2.value == test_series.iloc[-1] + 1
