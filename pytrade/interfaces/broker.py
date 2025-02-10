import abc

from pytrade.instruments import Granularity, Instrument
from pytrade.interfaces.data import IInstrumentData
from pytrade.interfaces.position import IPosition
from pytrade.models import Order


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

    @property
    @abc.abstractmethod
    def leverage(self) -> float:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_position(self, instrument: Instrument) -> IPosition:
        raise NotImplementedError()

    @abc.abstractmethod
    def close_position(self, instrument: Instrument):
        raise NotImplementedError()

    @abc.abstractmethod
    def order(self, order: Order):
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe(
        self, instrument: Instrument, granularity: Granularity
    ) -> IInstrumentData:
        raise NotImplementedError()
