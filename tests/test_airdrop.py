from unittest import mock
import importlib
import sqlite3


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
