import abc

from pytrade.interfaces.data import IInstrumentData
from pytrade.models.instruments import Granularity, Instrument
from pytrade.models.order import OrderRequest


class IBroker(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "order")
            and callable(subclass.order)
            and hasattr(subclass, "equity")
            and hasattr(subclass, "margin_available")
            or NotImplemented
        )

    @property
    @abc.abstractmethod
    def equity(self) -> float:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def margin_available(self) -> float:
        raise NotImplementedError()

    @abc.abstractmethod
    def order(self, order: OrderRequest):
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe(
        self, instrument: Instrument, granularity: Granularity
    ) -> IInstrumentData:
        raise NotImplementedError()
