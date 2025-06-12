from unittest import mock
import importlib
import sqlite3
import pytest

from cultist_chan_bot.airdrop_hunter import evaluate_airdrops, join_airdrop


def _setup(tmp_path):
    db_path = tmp_path / "test.db"
    import cultist_chan_bot.airdrop as ad
    importlib.reload(ad)
    ad.DB_PATH = db_path
    ad.init_db()
    return ad


def test_save_airdrop_history(tmp_path):
    ad = _setup(tmp_path)
    with mock.patch('cultist_chan_bot.airdrop.get_logger') as get_log:
        logger = get_log.return_value
        ad.save_airdrop_history('Drop1', 'joined', 1.0)
        logger.info.assert_called_once()
    with sqlite3.connect(ad.DB_PATH) as conn:
        rows = conn.execute(
            'SELECT name, status, joined_at FROM airdrop_log'
        ).fetchall()
    assert rows == [('Drop1', 'joined', 1.0)]


def test_get_airdrop_history(tmp_path):
    ad = _setup(tmp_path)
    ad.save_airdrop_history('A', 'joined', 1.0)
    ad.save_airdrop_history('B', 'skipped', 2.0)
    rows = ad.get_airdrop_history()
    assert rows == [('B', 'skipped', 2.0), ('A', 'joined', 1.0)]


@pytest.mark.asyncio
async def test_evaluate_airdrops_async():
    drops = [{"name": "A"}, {"name": "B"}]
    with mock.patch(
        "cultist_chan_bot.airdrop.airdrop_hunter.generate_reply",
        new=mock.AsyncMock(return_value='["A"]'),
    ) as gen:
        result = await evaluate_airdrops(drops)
    assert result == [drops[0]]
    gen.assert_awaited_once()


@pytest.mark.asyncio
async def test_join_airdrop_logs():
    drop = {"name": "Test"}
    with mock.patch(
        "cultist_chan_bot.airdrop.airdrop_hunter.log_airdrop",
        new=mock.AsyncMock(),
    ) as log:
        result = await join_airdrop(drop)
        log.assert_awaited_once_with(drop, "joined")
    assert result == {"name": "Test", "success": True}
