from fx_lib.events.typed_event import TypedEvent
from fx_lib.models.instruments import Candlestick


class CandlestickEvent(TypedEvent[Candlestick]):
    pass