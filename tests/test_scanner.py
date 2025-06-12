from unittest import mock

from cultist_chan_bot.scanner import evaluate_nft


def test_evaluate_nft_triggers_purchase():
    meta = {"name": "Cool"}
    with mock.patch(
        "cultist_chan_bot.scanner.query_llm",
        new=mock.AsyncMock(return_value="Yes indeed"),
    ) as q:
        assert evaluate_nft(meta) is True
        q.assert_called_once()


