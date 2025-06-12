from unittest import mock

import asyncio
import os
import signal
import pytest

from cultist_chan_bot import scheduler


def test_run_daily_hunt_executes_join(caplog):
    fetch = mock.Mock(return_value=[{"name": "Drop1"}, {"name": "Drop2"}])
    with mock.patch("cultist_chan_bot.scheduler.evaluate_airdrops", return_value=[{"name": "Drop2"}]) as eval_mock, \
         mock.patch("cultist_chan_bot.scheduler.join_airdrop", return_value={"name": "Drop2", "success": True}) as join_mock, \
         caplog.at_level("INFO"):
        scheduler.run_daily_hunt(fetch)
    eval_mock.assert_called_once_with(fetch.return_value)
    join_mock.assert_called_once_with({"name": "Drop2"})
    assert "Fetched 2 airdrops" in caplog.text
    assert "Joined Drop2 success=True" in caplog.text


@pytest.mark.asyncio
async def test_scheduler_shutdown(monkeypatch):
    fetch = mock.Mock(return_value=[])  # quick
    called = asyncio.Event()

    orig_stop = scheduler.stop_scheduler

    async def wrapped_stop() -> None:
        called.set()
        await orig_stop()

    monkeypatch.setattr(scheduler, "stop_scheduler", wrapped_stop)

    await scheduler.start_scheduler(fetch, interval=0.01)
    os.kill(os.getpid(), signal.SIGTERM)

    await asyncio.wait_for(called.wait(), 0.2)
