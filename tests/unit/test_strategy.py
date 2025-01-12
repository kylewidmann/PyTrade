import asyncio
import random
from datetime import datetime, timedelta
from typing import List
from unittest.mock import MagicMock, call, patch

import pytest

from pytrade.models.instruments import (
    MINUTES_MAP,
    CandleData,
    Candlestick,
    CandleSubscription,
    Granularity,
    FxInstrument,
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
    CandleSubscription(FxInstrument.EURUSD, Granularity.M5),
    CandleSubscription(FxInstrument.EURUSD, Granularity.M5),
    CandleSubscription(FxInstrument.EURUSD, Granularity.M15),
    CandleSubscription(FxInstrument.GBPUSD, Granularity.M5),
    CandleSubscription(FxInstrument.GBPUSD, Granularity.M5),
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


def get_updates():
    end_time = datetime.now()
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
    update_candles = get_updates()

    updates = TEST_UPDATES.copy()
    for candle in update_candles:
        strategy._update_instrument(candle)
        updates.remove(CandleSubscription(candle.instrument, candle.granularity))
        assert len(strategy._pending_updates) == len(updates)


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
    data_context = CandleData()

    strategy = _TestStrategy(broker, data_context)
    strategy.init()

    subscribe_calls = [
        call(s.instrument, s.granularity, strategy._update_instrument)
        for s in TEST_SUBCRIPTIONS
    ]

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

        await strategy.next()
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

            next_task = asyncio.create_task(strategy.next())
            assert not mock_next.called
            assert not next_task.done()

            send_strategy_updates(strategy)

            await asyncio.wait_for(next_task, timeout=0.2)
            assert mock_next.called
            assert next_task.done()
            assert len(strategy._pending_updates) == len(TEST_UPDATES)
            assert strategy._pending_updates == strategy._required_updates
            mock_next.reset_mock()
