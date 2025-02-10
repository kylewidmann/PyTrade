from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pandas as pd
from pandas import Timestamp

from pytrade.models import Order, TimeInForce, Trade


def test_order():
    instrument = "GOOG"
    size = 100
    stop = 101
    limit = 102
    order = Order(instrument, size, stop, limit)

    assert order.instrument == instrument
    assert order.size == size
    assert order.stop == stop
    assert order.limit == limit
    assert order.time_in_force == TimeInForce.GOOD_TILL_CANCELLED
    assert order.is_long is True
    assert order.is_contingent is False
    assert order.take_profit_on_fill is None
    assert order.stop_loss_on_fill is None
    assert order.trailing_stop_loss_on_fill is None
    assert order.pricebound is None
    assert order.parent_trade is None


def test_order_equality():
    order = Order("GOOG", 100, 101, 102)
    order2 = Order("GOOG", 100, 101, 102)

    assert order == order
    assert order2 != order


def test_order_reudce():
    new_size = 50
    order = Order("GOOG", 100, 101, 102)
    order.resize(new_size)

    assert order.size == new_size


def test_trade():
    instrument = "GOOG"
    size = 100
    entry_price = 98.90
    last_price = 100
    entry_time = Timestamp(datetime.now())
    exit_price = 110.50
    exit_time = entry_time + timedelta(days=1, hours=2)
    data = MagicMock()
    data.last_price = last_price
    df = pd.DataFrame(
        {"Timestamp": [entry_time, exit_time], "Close": [entry_price, exit_price]}
    )
    df = df.set_index("Timestamp")
    data.df = df

    trade = Trade(instrument, size, entry_price, entry_time, data)

    pl = (last_price - entry_price) * 100
    assert trade.instrument == instrument
    assert trade.size == size
    assert trade.entry_price == entry_price
    assert trade.exit_price is None
    assert trade.tag is None
    assert trade.entry_time == entry_time
    assert trade.exit_time is None
    assert trade.is_long is True
    assert trade.is_short is False
    assert trade.pl == pl
    assert trade.pl_pct == (last_price / entry_price - 1) * 100
    assert trade.value == size * last_price
    assert trade.sl is None
    assert trade.tp is None

    trade.close(exit_price, exit_time)

    assert trade.exit_price == exit_price
    assert trade.exit_time == exit_time
    assert trade.pl == (exit_price - entry_price) * size
    assert trade.pl_pct == (exit_price / entry_price - 1) * 100
    assert trade.value == size * exit_price


def test_trade_reduce():
    instrument = "GOOG"
    size = 100
    entry_price = 98.90
    last_price = 100
    entry_time = Timestamp(datetime.now())
    exit_price = 110.50
    exit_time = entry_time + timedelta(days=1, hours=2)
    data = MagicMock()
    data.last_price = last_price
    df = pd.DataFrame(
        {"Timestamp": [entry_time, exit_time], "Close": [entry_price, exit_price]}
    )
    df = df.set_index("Timestamp")
    data.df = df

    trade = Trade(instrument, size, entry_price, entry_time, data)

    trade.reduce(50)

    assert trade.size == 50
