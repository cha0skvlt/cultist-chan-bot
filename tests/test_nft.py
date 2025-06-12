from unittest import mock

import json
import sqlite3

from cultist_chan_bot.nft import scan_nfts, run_daily_nft_scan


def test_scan_nfts():
    data = [{"id": 1}, {"id": 2}]
    responses = ["yes", "no"]
    with mock.patch(
        "cultist_chan_bot.scanner.query_llm",
        new=mock.AsyncMock(side_effect=responses),
    ) as q, \
        mock.patch("cultist_chan_bot.nft.generate_persona_reply", return_value="ok"), \
        mock.patch("cultist_chan_bot.nft.log_nft_purchase"):
        result = scan_nfts(lambda: data)
    assert result == [data[0]]
    assert q.call_count == 2


def test_purchase_nft(tmp_path):
    db_path = tmp_path / "db.sqlite"
    import importlib
    from cultist_chan_bot import db
    importlib.reload(db)
    db.init_db(str(db_path))
    import cultist_chan_bot.nft as nft_mod
    importlib.reload(nft_mod)
    nft = {"id": 1}
    with mock.patch("cultist_chan_bot.nft.generate_persona_reply", return_value="ok") as gen:
        result = nft_mod.purchase_nft(nft)
    assert result == "ok"
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT status, metadata FROM nft_purchases").fetchone()
    assert row[0] == "success"
    assert json.loads(row[1]) == nft
    gen.assert_called_once_with("nft_purchase", {"nft": nft})


def test_scan_nfts_triggers_purchase():
    data = [{"id": 1}, {"id": 2}]
    with mock.patch("cultist_chan_bot.nft.evaluate_nft", return_value=True) as eval_mock, \
        mock.patch("cultist_chan_bot.nft.purchase_nft") as buy:
        result = scan_nfts(lambda: data)
    assert result == data
    assert eval_mock.call_count == 2
    buy.assert_has_calls([mock.call(data[0]), mock.call(data[1])])


def test_run_daily_nft_scan(caplog):
    with mock.patch("cultist_chan_bot.nft.scan_nfts") as scan, \
        caplog.at_level("INFO"):
        run_daily_nft_scan()
    scan.assert_called_once()
    assert "NFT scan started" in caplog.text
    assert "NFT scan finished" in caplog.text

