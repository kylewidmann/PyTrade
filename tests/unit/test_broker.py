from unittest.mock import Mock

from pytrade.broker import Broker
from pytrade.instruments import FxInstrument
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


def test_get_data():
    pass
