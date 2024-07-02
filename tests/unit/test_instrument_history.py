
from datetime import datetime, timedelta
import random
import time
from timeit import timeit

import pandas as pd
import pytest

from fx_lib.models.granularity import Granularity, MINUTES_MAP
from fx_lib.models.instruments import Candlestick
from fx_lib.models.instruments import Instrument, InstrumentHistory, COLUMNS

def get_candles(count: int, granularity: Granularity):
    start_time = datetime.now()
    _delta = MINUTES_MAP[granularity]
    return[
        Candlestick(
            Instrument.EURUSD,
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            start_time + timedelta(minutes=_delta * i),
        )
        for i
        in range(count)
    ]

def candles_to_data(candles: list[Candlestick]):
    return [
            [
                candlestick.timestamp,
                candlestick.instrument,
                candlestick.open,
                candlestick.high,
                candlestick.low,
                candlestick.close
            ]
            for candlestick 
            in candles
        ]


def test_max_history():
    max_history = 10

    history = InstrumentHistory(max_history=max_history)

    dummy_candles = get_candles(max_history+1, Granularity.M5)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index("Timestamp", inplace=True)
    for candle in dummy_candles[:max_history]:
        history.update(candle)

    assert len(history.df) == max_history
    history.update(dummy_candles[-1])
    assert len(history.df) == max_history

def test_fifo():
    max_history = 10

    history = InstrumentHistory(max_history=max_history)

    dummy_candles = get_candles(max_history+1, Granularity.M5)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index("Timestamp", inplace=True)
    for candle in dummy_candles[:max_history]:
        history.update(candle)

    history.update(dummy_candles[-1])
    assert history.df.equals(final_df)

@pytest.mark.parametrize("granularity", [Granularity.M1, Granularity.M5, Granularity.H1, Granularity.H4])
def test_shift_freq(granularity: Granularity):
    max_history = 10

    history = InstrumentHistory(max_history=max_history)

    dummy_candles = get_candles(max_history+1, granularity)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index("Timestamp", inplace=True)
    for candle in dummy_candles[:max_history]:
        history.update(candle)

    history.update(dummy_candles[-1])
    assert history.df.equals(final_df)

@pytest.mark.parametrize("scale", [10, 1000, 10000])
def test_update_execution_time(scale: int):

    history = InstrumentHistory(max_history=scale)

    dummy_candles = get_candles(scale+1, Granularity.M1)
    final_df = pd.DataFrame(candles_to_data(dummy_candles[1:]), columns=COLUMNS)
    final_df.set_index("Timestamp", inplace=True)
    for candle in dummy_candles[:scale]:
        history.update(candle)

    start_time = time.time()
    history.update(dummy_candles[-1])
    run_time = time.time() - start_time
    assert run_time < .002
