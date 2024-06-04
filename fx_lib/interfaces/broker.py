import abc


class IBroker(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "new_order")
            and callable(subclass.new_order)
            and hasattr(subclass, "equity")
            and hasattr(subclass, "margin_available")
            or NotImplemented
        )

    @abc.abstractmethod
    def new_order(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def equity(self) -> float:
        raise NotImplementedError
        return self._cash + sum(trade.pl for trade in self.trades)

    @property
    @abc.abstractmethod
    def margin_available(self) -> float:
        raise NotImplementedError
        # From https://github.com/QuantConnect/Lean/pull/3768
        margin_used = sum(trade.value / self._leverage for trade in self.trades)
        return max(0, self.equity - margin_used)
