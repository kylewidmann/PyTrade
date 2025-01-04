from pytrade.events.typed_event import TypedEvent
from pytrade.models.instruments import Candlestick


class CandlestickEvent(TypedEvent[Candlestick]):
    pass