from typing import List

from pytrade.instruments import Granularity, Instrument
from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.client import IClient
from pytrade.models import Order


class Broker(IBroker):

    def __init__(self, client: IClient):
        self.client = client
        self._orders: List[Order] = []

    @property
    def equity(self) -> float:
        raise NotImplementedError

    @property
    def margin_available(self) -> float:
        raise NotImplementedError

    def order(self, order: Order):
        self._orders.append(order)

    def process_orders(self):
        for order in self._orders:
            self.client.order(order)

        self._orders.clear()

    def subscribe(self, instrument: Instrument, granularity: Granularity):
        # self.client.subscribe(instrument, granularity)
        pass
