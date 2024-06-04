from fx_lib.interfaces.broker import IBroker


class Broker(IBroker):

    def __init__(self, client):
        self.client = client

    def new_order(self, size, limit, stop, sl, tp, tag):
        raise NotImplementedError

    @property
    def equity(self) -> float:
        raise NotImplementedError
        # return self._cash + sum(trade.pl for trade in self.trades)

    @property
    def margin_available(self) -> float:
        raise NotImplementedError
        # From https://github.com/QuantConnect/Lean/pull/3768
        # margin_used = sum(trade.value / self._leverage for trade in self.trades)
        # return max(0, self.equity - margin_used)
