import sqlite3

import cultist_chan_bot.db as db


def test_log_airdrop(tmp_path):
    db_path = tmp_path / "test.db"
    db.init_db(str(db_path))
    drop = {"name": "DropX", "value": 5}
    db.log_airdrop(drop, "joined")
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name, status FROM airdrops WHERE name = ?", ("DropX",)
        ).fetchall()
    assert rows == [("DropX", "joined")]
    with sqlite3.connect(db_path) as conn:
        rows_by_status = conn.execute(
            "SELECT name FROM airdrops WHERE status = ?", ("joined",)
        ).fetchall()
    assert ("DropX",) in rows_by_status


def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "new.db"
    db.init_db(str(db_path))
    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert {"airdrop_events", "nft_events", "users"}.issubset(tables)
