

from typing import Callable
from unittest.mock import Mock

from multimethod import multimethod
from pytrade.broker import FxBroker
from pytrade.interfaces.client import IClient
from pytrade.models.instruments import Candlestick, Granularity, Instrument
from pytrade.models.order import MarketOrderRequest, OrderRequest, TimeInForce

def test_buy_order():
    client = Mock()
    broker = FxBroker(client)

    assert len(broker._pending_orders) == 0

    broker.order(OrderRequest(
        Instrument.GBPUSD,
        10,
        TimeInForce.GOOD_TILL_CANCELLED
    ))

    assert len(broker._pending_orders) == 1

def test_sell_order():
    client = Mock()
    broker = FxBroker(client)

    assert len(broker._pending_orders) == 0

    broker.order(OrderRequest(
        Instrument.GBPUSD,
        -10,
        TimeInForce.GOOD_TILL_CANCELLED
    ))

    assert len(broker._pending_orders) == 1

def test_process_orders():
    client = Mock()
    broker = FxBroker(client)    

    broker.order(OrderRequest(
        Instrument.GBPUSD,
        10,
        TimeInForce.GOOD_TILL_CANCELLED
    ))

    assert len(broker._pending_orders) == 1

    broker.process_orders()

    assert len(broker._pending_orders) == 0
    assert client.order.call_count == 1

def test_buy():
    pass

def test_sell():
    pass

def test_get_data():
    pass