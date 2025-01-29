from datetime import datetime, timedelta

import pytest
from pandas import Timestamp

from pytrade.models import Order, Position, TimeInForce, Trade


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
    entry_time = Timestamp(datetime.now())
    trade = Trade(instrument, size, entry_price, entry_time)

    exit_price = 110.50
    exit_time = entry_time + timedelta(days=1, hours=2)

    assert trade.instrument == instrument
    assert trade.size == size
    assert trade.entry_price == entry_price
    assert trade.exit_price is None
    assert trade.tag is None
    assert trade.entry_time == entry_time
    assert trade.exit_time is None
    assert trade.is_long is True
    assert trade.is_short is False
    assert trade.pl == 0
    assert trade.pl_pct == 0
    assert trade.value == 0
    assert trade.sl is None
    assert trade.tp is None

    trade.close(exit_price, exit_time)

    assert trade.exit_price == exit_price
    assert trade.exit_time == exit_time
    assert trade.pl == (exit_price - entry_price) * size
    assert trade.pl_pct == exit_price / entry_price - 1
    assert trade.value == size * exit_price


def test_trade_reduce():
    instrument = "GOOG"
    size = 100
    entry_price = 98.90
    entry_time = Timestamp(datetime.now())
    trade = Trade(instrument, size, entry_price, entry_time)

    trade.reduce(50)

    assert trade.size == 50


def test_position():
    instrument_1 = "ABC"
    instrument_2 = "GOOG"
    abc_trades = [
        Trade(instrument_1, 100, 90, Timestamp(datetime.now() - timedelta(days=1))),
        Trade(instrument_1, 150, 85, Timestamp(datetime.now())),
    ]
    goog_trades = [
        Trade(instrument_2, 100, 90, Timestamp(datetime.now() - timedelta(hours=12))),
        Trade(instrument_2, 200, 100, Timestamp(datetime.now() - timedelta(hours=3))),
    ]
    trades = abc_trades + goog_trades

    position = Position(instrument_2, trades)

    assert len(position.trades) == 2
    assert position.size == 300
    assert position.pl == 0
    assert position.pl_pct == 0
    assert position.is_long is True
    assert position.is_short is False


def test_position_close():
    instrument_1 = "ABC"
    instrument_2 = "GOOG"
    abc_trades = [
        Trade(instrument_1, 100, 90, Timestamp(datetime.now() - timedelta(days=1))),
        Trade(instrument_1, 150, 85, Timestamp(datetime.now())),
    ]
    goog_trades = [
        Trade(instrument_2, 100, 90, Timestamp(datetime.now() - timedelta(hours=12))),
        Trade(instrument_2, 200, 100, Timestamp(datetime.now() - timedelta(hours=3))),
    ]
    trades = abc_trades + goog_trades

    position = Position(instrument_2, trades)

    position.close(110, Timestamp(datetime.now()))

    assert position.size == 300
    assert position.pl == 4000
    assert position.pl_pct == pytest.approx(0.14, 1e-2)
