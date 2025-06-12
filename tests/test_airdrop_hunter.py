from unittest import mock

from cultist_chan_bot.airdrop_hunter import evaluate_airdrops, join_airdrop


def test_evaluate_airdrops_returns_selected():
    drops = [
        {"name": "DropA", "desc": "A"},
        {"name": "DropB", "desc": "B"},
        {"name": "DropC", "desc": "C"},
    ]
    reply = '["DropA", "DropC"]'


    with mock.patch(
        "cultist_chan_bot.airdrop_hunter.query_llm",
        new=mock.AsyncMock(return_value=reply),
    ) as q:
        result = evaluate_airdrops(drops)

        assert result == [drops[0], drops[2]]
        q.assert_called_once()




def test_join_airdrop_simulation(caplog):
    drop = {"name": "Test"}
    with caplog.at_level("INFO"), \
         mock.patch("cultist_chan_bot.airdrop_hunter.log_airdrop") as log:
        result = join_airdrop(drop)
        log.assert_called_once_with(drop, "joined")

    assert result == {"name": "Test", "success": True}
    assert "Joining airdrop: Test" in caplog.text


