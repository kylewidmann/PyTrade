from typing import List, Tuple

from pytrade.data import CandleData
from pytrade.instruments import Granularity, Instrument
from pytrade.interfaces.broker import IBroker
from pytrade.interfaces.client import IClient
from pytrade.interfaces.data import IInstrumentData
from pytrade.interfaces.position import IPosition
from pytrade.logging import get_logger
from pytrade.models import Order


class Broker(IBroker):

    def __init__(self, client: IClient , max_history = 100):
        self.client = client
        self._orders: List[Order] = []
        self._data_context = CandleData(max_size=max_history)
        self._subscriptions: list[Tuple[Instrument, Granularity]] = []
        self.logger = get_logger()

    @property
    def equity(self) -> float:
        return self.client.account.equity

    @property
    def margin_available(self) -> float:
        return self.client.account.margin_available

    @property
    def leverage(self) -> float:
        return self.client.account.leverage

    def get_position(self, instrument: Instrument) -> IPosition:
        return self.client.get_position(instrument)

    def close_position(self, instrument: Instrument):
        return self.client.close_position(instrument)

    def order(self, order: Order):
        self._orders.append(order)

    def process_orders(self):
        self.logger.debug(f"Processing {len(self._orders)} orders.")
        for order in self._orders:
            self.client.order(order)

        self._orders.clear()
        self.logger.debug("Orders cleared.")

    def load_instrument_candles(
        self, instrument: Instrument, granularity: Granularity, count: int
    ):
        key = (instrument, granularity)
        self.logger.debug(f"Loading candles for {key}")

        if key in self._subscriptions:
            raise RuntimeError(
                f"Consumers are already subscribed to {instrument}[{granularity.value}], \
can not populate historical data."
            )

        instrument_data = self._data_context.get(instrument, granularity)
        if len(instrument_data.df) < count:
            instrument_data.clear()
            candles = self.client.get_candles(instrument, granularity, count)
            self.logger.debug(f"Loading candles for {instrument_data}.")
            for candle in candles:
                instrument_data.update(candle)

    def subscribe(
        self, instrument: Instrument, granularity: Granularity
    ) -> IInstrumentData:

        key = (instrument, granularity)
        self.logger.debug(f"Subscribing to candles for {key}")

        instrument_data = self._data_context.get(instrument, granularity)

        # If we are already tracking this pair/granularity no need to resubscribe
        if key not in self._subscriptions:
            self.client.subscribe(instrument, granularity, self._data_context.update)
            self._subscriptions.append(key)

        return instrument_data
