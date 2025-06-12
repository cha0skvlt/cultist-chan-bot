from unittest import mock
import json

import pytest
from cultist_chan_bot.persona import generate_persona_reply, PROMPT_FILE



@pytest.mark.asyncio
async def test_generate_persona_reply_formatting():
    context = {"text": "hi"}
    with mock.patch(
        "cultist_chan_bot.llm.persona.generate_reply",
        new=mock.AsyncMock(return_value="yo"),
    ) as q, \
         mock.patch("cultist_chan_bot.llm.persona.retrieve_context", return_value=[]), \
         mock.patch("cultist_chan_bot.llm.persona.save_interaction"):
        result = await generate_persona_reply("message", context)
        assert result == "yo"
        expected = PROMPT_FILE.read_text() + "\n" + json.dumps({"event": "message", "context": context})
        q.assert_awaited_once_with(expected)


@pytest.mark.asyncio
async def test_log_telemetry(tmp_path):
    db_path = tmp_path / "t.db"
    import importlib
    import cultist_chan_bot.db as db
    importlib.reload(db)
    db.init_db(str(db_path))
    with mock.patch(
        "cultist_chan_bot.llm.persona.generate_reply",
        new=mock.AsyncMock(return_value="ok"),
    ), \
         mock.patch("cultist_chan_bot.llm.persona.retrieve_context", return_value=[]), \
         mock.patch("cultist_chan_bot.llm.persona.save_interaction"):
        result = await generate_persona_reply("event", {"a": 1})
        assert result == "ok"
        import sqlite3
        import json as js
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT event, payload, response FROM telemetry"
            ).fetchone()
        assert row[0] == "event"
        assert js.loads(row[1]) == {"a": 1}
        assert row[2] == "ok"


@pytest.mark.asyncio
async def test_generate_reply_with_memory():
    context = {"user_id": 5, "text": "yo"}
    memory = [
        {"message": "hi", "reply": "hey"},
        {"message": "sup", "reply": "ok"},
    ]
    with mock.patch("cultist_chan_bot.llm.persona.retrieve_context", return_value=memory), \
         mock.patch(
             "cultist_chan_bot.llm.persona.generate_reply",
             new=mock.AsyncMock(return_value="ok"),
         ) as q, \
         mock.patch("cultist_chan_bot.llm.persona.save_interaction"):
        await generate_persona_reply("msg", context)
        prompt = q.call_args[0][0]
    assert "User: hi\nBot: hey" in prompt
    assert "User: sup\nBot: ok" in prompt


@pytest.mark.asyncio
async def test_save_reply_to_memory():
    context = {"user_id": 9, "text": "hello"}
    with mock.patch(
        "cultist_chan_bot.llm.persona.generate_reply",
        new=mock.AsyncMock(return_value="hi"),
    ), \
         mock.patch("cultist_chan_bot.llm.persona.retrieve_context", return_value=[]), \
         mock.patch("cultist_chan_bot.llm.persona.save_interaction") as save:
        result = await generate_persona_reply("msg", context)
    assert result == "hi"
    save.assert_called_once_with(9, "hello", "hi")
