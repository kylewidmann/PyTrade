import random
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock

import pytest

from pytrade.broker import Broker
from pytrade.instruments import MINUTES_MAP, Candlestick, FxInstrument, Granularity
from pytrade.models import Order


def _get_candles(
    instrument: FxInstrument,
    granularity: Granularity,
    count: int,
    end_time: datetime = datetime.now(tz=timezone.utc),
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


def test_buy_order():
    client = Mock()
    broker = Broker(client)

    assert len(broker._orders) == 0

    broker.order(Order(FxInstrument.GBPUSD, 10))

    assert len(broker._orders) == 1


def test_sell_order():
    client = Mock()
    broker = Broker(client)

    assert len(broker._orders) == 0

    broker.order(Order(FxInstrument.GBPUSD, -10))

    assert len(broker._orders) == 1


def test_process_orders():
    client = Mock()
    broker = Broker(client)

    broker.order(Order(FxInstrument.GBPUSD, 10))

    assert len(broker._orders) == 1

    broker.process_orders()

    assert len(broker._orders) == 0
    assert client.order.call_count == 1


def test_buy():
    pass


def test_sell():
    pass


def test_subscribe():
    client = MagicMock()
    broker = Broker(client)

    assert len(broker._subscriptions) == 0
    assert client.subscribe.call_count == 0

    broker.subscribe(FxInstrument.EURUSD, Granularity.M1)

    assert len(broker._subscriptions) == 1
    assert client.subscribe.call_count == 1
    assert len(broker._data_context._data) == 1

    broker.subscribe(FxInstrument.EURUSD, Granularity.M1)

    assert len(broker._subscriptions) == 1
    assert client.subscribe.call_count == 1
    assert len(broker._data_context._data) == 1

    broker.subscribe(FxInstrument.GBPUSD, Granularity.M1)

    assert len(broker._subscriptions) == 2
    assert client.subscribe.call_count == 2
    assert len(broker._data_context._data) == 2


def test_load_instrument_candles():
    client = MagicMock()
    client.get_candles.side_effect = _get_candles
    broker = Broker(client)

    instrument = FxInstrument.EURUSD
    granularity = Granularity.M1

    instrument_data = broker._data_context.get(instrument, granularity)
    assert len(instrument_data.df) == 0

    broker.load_instrument_candles(instrument, granularity, 10)
    assert len(instrument_data.df) == 10

    broker.load_instrument_candles(instrument, granularity, 5)
    assert len(instrument_data.df) == 10

    broker.load_instrument_candles(instrument, granularity, 20)
    assert len(instrument_data.df) == 20


def test_load_instrument_candles_after_subscribing():
    client = MagicMock()
    client.get_candles.side_effect = _get_candles
    broker = Broker(client)

    instrument = FxInstrument.EURUSD
    granularity = Granularity.M1

    assert len(broker._subscriptions) == 0
    assert client.subscribe.call_count == 0

    broker.subscribe(instrument, granularity)

    assert len(broker._subscriptions) == 1
    assert client.subscribe.call_count == 1
    assert len(broker._data_context._data) == 1

    instrument_data = broker._data_context.get(instrument, granularity)
    assert len(instrument_data.df) == 0

    with pytest.raises(RuntimeError) as e:
        broker.load_instrument_candles(instrument, granularity, 10)

    assert (
        e.value.args[0]
        == "Consumers are already subscribed to FxInstrument.EURUSD[M1], can not populate historical data."
    )
