import random
import time
from datetime import datetime, timedelta

import pandas as pd
import pytest

from pytrade.data import COLUMNS, INDEX, InstrumentCandles
from pytrade.instruments import MINUTES_MAP, Candlestick, FxInstrument, Granularity


def get_candles(count: int, granularity: Granularity):
    start_time = datetime.now()
    _delta = MINUTES_MAP[granularity]
    return [
        Candlestick(
            FxInstrument.EURUSD,
            granularity,
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            start_time + timedelta(minutes=_delta * i),
        )
        for i in range(count)
    ]


def candles_to_data(candles: list[Candlestick]):
    return [
        [
            candlestick.timestamp,
            candlestick.instrument,
            candlestick.open,
            candlestick.high,
            candlestick.low,
            candlestick.close,
        ]
        for candlestick in candles
    ]


def test_max_history():
    max_history = 10

    history = InstrumentCandles(max_size=max_history)

    dummy_candles = get_candles(max_history + 1, Granularity.M5)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index(INDEX, inplace=True)
    for candle in dummy_candles[:max_history]:
        history.update(candle)

    assert len(history.df) == max_history
    history.update(dummy_candles[-1])
    assert len(history.df) == max_history


def test_fifo():
    max_history = 10

    history = InstrumentCandles(max_size=max_history)

    dummy_candles = get_candles(max_history + 1, Granularity.M5)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index(INDEX, inplace=True)
    for candle in dummy_candles[:max_history]:
        history.update(candle)

    history.update(dummy_candles[-1])
    assert history.df.equals(final_df)


@pytest.mark.parametrize(
    "granularity", [Granularity.M1, Granularity.M5, Granularity.H1, Granularity.H4]
)
def test_shift_freq(granularity: Granularity):
    max_history = 10

    history = InstrumentCandles(max_size=max_history)

    dummy_candles = get_candles(max_history + 1, granularity)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index(INDEX, inplace=True)
    for candle in dummy_candles[:max_history]:
        history.update(candle)

    history.update(dummy_candles[-1])
    assert history.df.equals(final_df)


@pytest.mark.parametrize("scale", [10, 1000, 10000])
def test_update_execution_time(scale: int):

    dummy_candles = get_candles(scale + 1, Granularity.M1)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index(INDEX, inplace=True)

    initial_df = pd.DataFrame.from_records(
        [c.to_dict() for c in dummy_candles[:scale]], columns=COLUMNS
    )
    history = InstrumentCandles(data=initial_df, max_size=scale)

    start_time = time.time()
    history.update(dummy_candles[-1])
    run_time = time.time() - start_time
    assert run_time < 0.003


def test_update_wrong_instrument():
    dummy_candles = get_candles(2, Granularity.M1)

    with pytest.raises(RuntimeError):
        history = InstrumentCandles(max_size=10)
        first_candle = dummy_candles[0]
        second_candle = dummy_candles[1]
        second_candle.instrument = FxInstrument.GBPUSD

        assert first_candle.instrument != second_candle.instrument

        history.update(first_candle)
        history.update(second_candle)


def test_update_wrong_granularity():
    dummy_candles = get_candles(2, Granularity.M1)

    with pytest.raises(RuntimeError):
        history = InstrumentCandles(max_size=10)
        first_candle = dummy_candles[0]
        second_candle = dummy_candles[1]
        second_candle.granularity = Granularity.H1

        assert first_candle.granularity != second_candle.granularity

        history.update(first_candle)
        history.update(second_candle)
