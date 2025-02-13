from unittest.mock import MagicMock, Mock

from pytrade.broker import Broker
from pytrade.instruments import FxInstrument, Granularity
from pytrade.models import Order


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
