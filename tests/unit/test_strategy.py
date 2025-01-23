import random
from datetime import datetime, timedelta
from typing import List
from unittest.mock import MagicMock, call, patch

import pytest
from pandas import Timestamp

from pytrade.data import CandleData
from pytrade.instruments import (
    MINUTES_MAP,
    Candlestick,
    CandleSubscription,
    FxInstrument,
    Granularity,
)
from pytrade.strategy import FxStrategy

TEST_SUBCRIPTIONS = [
    CandleSubscription(FxInstrument.EURUSD, Granularity.M5),
    CandleSubscription(FxInstrument.EURUSD, Granularity.M15),
    CandleSubscription(FxInstrument.GBPUSD, Granularity.M5),
    CandleSubscription(FxInstrument.GBPUSD, Granularity.M15),
]

TEST_UPDATES = [
    CandleSubscription(FxInstrument.EURUSD, Granularity.M5),
    CandleSubscription(FxInstrument.EURUSD, Granularity.M15),
    CandleSubscription(FxInstrument.GBPUSD, Granularity.M5),
    CandleSubscription(FxInstrument.GBPUSD, Granularity.M15),
]


def get_candles(
    count: int, instrument: FxInstrument, granularity: Granularity, end_time: datetime
) -> list[Candlestick]:
    _delta = MINUTES_MAP[granularity]
    return [
        Candlestick(
            instrument,
            granularity,
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            random.uniform(0, 10),
            end_time - timedelta(minutes=_delta * i),
        )
        for i in range(count)
    ]


def get_updates(freq: str):
    end_time = Timestamp(datetime.now()).ceil(freq=freq)
    update_candles: list[Candlestick] = []
    max_interval = max(MINUTES_MAP[sub.granularity] for sub in TEST_SUBCRIPTIONS)
    for subscription in TEST_SUBCRIPTIONS:
        num_candles = int(max_interval / MINUTES_MAP[subscription.granularity])
        update_candles += get_candles(
            num_candles, subscription.instrument, subscription.granularity, end_time
        )

    update_candles.sort(key=lambda c: c.timestamp)

    return update_candles


def send_strategy_updates(strategy: FxStrategy):
    update_candles = get_updates(strategy._update_frequency)
    mock_instrument_data = MagicMock()

    for candle in update_candles:
        mock_instrument_data.instrument = candle.instrument
        mock_instrument_data.granularity = candle.granularity
        mock_instrument_data.timestamp = Timestamp(candle.timestamp)
        strategy._handle_update(mock_instrument_data)


class _TestStrategy(FxStrategy):

    @property
    def subscriptions(self) -> List[CandleSubscription]:
        return TEST_SUBCRIPTIONS

    def _init(self):
        pass

    def _next(self):
        pass


def test_monitor_instruments():
    broker = MagicMock()
    broker.subscribe.side_effect = MagicMock()
    data_context = CandleData()

    strategy = _TestStrategy(broker, data_context)
    strategy.init()

    subscribe_calls = [call(s.instrument, s.granularity) for s in TEST_SUBCRIPTIONS]

    broker.subscribe.assert_has_calls(subscribe_calls)


def test_instrument_updates():
    broker = MagicMock()
    data_context = CandleData()

    strategy = _TestStrategy(broker, data_context)
    with patch.object(strategy, "_updates_complete", MagicMock()) as mock_updates_event:
        strategy.init()

        assert strategy._pending_updates == strategy._required_updates

        send_strategy_updates(strategy)

        assert strategy._pending_updates == []
        assert mock_updates_event.set.called


@pytest.mark.asyncio
async def test_strategy_next():
    broker = MagicMock()
    data_context = CandleData()

    strategy = _TestStrategy(broker, data_context)
    with patch.object(strategy, "_next", MagicMock()) as mock_next:
        strategy.init()

        assert not mock_next.called

        send_strategy_updates(strategy)

        strategy.next()
        assert len(strategy._pending_updates) == len(TEST_UPDATES)
        assert strategy._pending_updates == strategy._required_updates


@pytest.mark.asyncio
async def test_strategy_waits_for_updates():
    broker = MagicMock()
    data_context = CandleData()

    strategy = _TestStrategy(broker, data_context)
    iterations = 2
    with patch.object(strategy, "_next", MagicMock()) as mock_next:
        strategy.init()
        for i in range(iterations):

            strategy.next()
            assert not mock_next.called

            send_strategy_updates(strategy)
            strategy.next()

            assert mock_next.called
            assert len(strategy._pending_updates) == len(TEST_UPDATES)
            assert strategy._pending_updates == strategy._required_updates
            mock_next.reset_mock()
