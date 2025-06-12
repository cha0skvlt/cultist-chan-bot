from unittest import mock



from cultist_chan_bot import commands


def test_status_uses_persona_reply():
    with mock.patch('cultist_chan_bot.commands.generate_persona_reply', return_value='ok') as gen:
        result = commands.status(scans=1, purchases=2, donations=3, timestamp=4)

        assert result == 'ok'
        gen.assert_called_once_with('status', {
            'scans': 1,
            'purchases': 2,
            'donations': 3,
            'timestamp': 4,
        })


def test_persona_airdrop_reply():
    drop = {"name": "DropZ", "value": 10}

    with mock.patch(
        "cultist_chan_bot.commands.join_airdrop", return_value={"name": "DropZ", "success": True}
    ) as join_mock, mock.patch(
        "cultist_chan_bot.commands.generate_persona_reply", return_value="msg"

    ) as persona_mock:
        result = commands.join_airdrop_action(drop)
        assert result == "msg"
        join_mock.assert_called_once_with(drop)
        persona_mock.assert_called_once_with("airdrop_joined", {"name": "DropZ", "drop": drop})



def test_log_stats_command(tmp_path):
    db_path = tmp_path / "db.sqlite"
    import importlib
    import cultist_chan_bot.db as db_mod
    importlib.reload(db_mod)
    db_mod.init_db(str(db_path))
    db_mod.log_airdrop({"name": "A"}, "joined")
    db_mod.log_airdrop({"name": "B"}, "skipped")
    db_mod.log_telemetry("ev1", {}, "r1")
    db_mod.log_telemetry("ev2", {}, "r2")
    db_mod.log_telemetry("ev2", {}, "r3")

    with mock.patch.object(commands, "ADMIN_IDS", {42}), \
         mock.patch(
            "cultist_chan_bot.commands.generate_persona_reply", return_value="stats"
        ) as gen:
        result = commands.log_stats(42)

    assert result == "stats"
    gen.assert_called_once_with(
        "log_stats_summary",
        {"airdrops": 1, "replies": 3, "events": 2},
    )


def test_onboarding_message(tmp_path):
    seen = tmp_path / "seen.txt"
    import importlib
    import cultist_chan_bot.commands as cmds
    importlib.reload(cmds)
    cmds.SEEN_USERS_FILE = seen
    cmds._SEEN_USERS = set()
    with mock.patch.object(cmds, "generate_persona_reply", return_value="welcome") as gen:
        msg = cmds.check_onboarding_message(1, "hello", username="bob")
        assert msg == "welcome"
        gen.assert_called_once_with("onboarding", {"user": "bob"})
        assert seen.read_text().strip() == "1"
        gen.reset_mock()
        assert cmds.check_onboarding_message(1, "hi") == ""
        gen.assert_not_called()


def test_airdrops_command_response(tmp_path):
    db_path = tmp_path / "db.sqlite"
    import importlib
    import cultist_chan_bot.db as db_mod
    importlib.reload(db_mod)
    db_mod.init_db(str(db_path))
    db_mod.log_airdrop({"name": "A"}, "joined")
    db_mod.log_airdrop({"name": "B"}, "skipped")
    history = db_mod.get_airdrop_history()
    import cultist_chan_bot.commands as cmds
    importlib.reload(cmds)

    with mock.patch("cultist_chan_bot.commands.generate_persona_reply", return_value="rep") as gen:
        result = cmds.airdrops()

        assert result == "rep"
        gen.assert_called_once_with("airdrops_history", {"airdrops": history})


