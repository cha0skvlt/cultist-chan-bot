import importlib
from unittest import mock

MODULES = [
    'cultist_chan_bot.bot',
    'cultist_chan_bot.config',
    'cultist_chan_bot.scheduler',
    'cultist_chan_bot.db',
    'cultist_chan_bot.ton',
    'cultist_chan_bot.scanner',
    'cultist_chan_bot.buyer',
    'cultist_chan_bot.airdrop_hunter',
    'cultist_chan_bot.memory',
    'cultist_chan_bot.telegram_bot',
    'cultist_chan_bot.commands',
    'cultist_chan_bot.logger',
    'cultist_chan_bot.llm',
    'cultist_chan_bot.persona',
    'cultist_chan_bot.nft',

]

def test_imports():
    for mod in MODULES:
        assert importlib.import_module(mod)


def test_config_loading(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        """
TELEGRAM_TOKEN: tok
DB_PATH: sample.db
LLM_URL: http://llm
MEMORY_PATH: mem.json
LOG_LEVEL: DEBUG
"""
    )

    import cultist_chan_bot.config as cfg

    with mock.patch.object(cfg, "CONFIG_FILE", cfg_file):
        settings = cfg.load_config()

    assert settings.TELEGRAM_TOKEN == "tok"
    assert settings.DB_PATH == "sample.db"
    assert settings.LLM_URL == "http://llm"
    assert settings.MEMORY_PATH == "mem.json"
    assert settings.LOG_LEVEL == "DEBUG"


def test_logger_format():
    import io
    import importlib
    import sys
    from cultist_chan_bot import logger as log_mod

    buf = io.StringIO()
    with mock.patch.object(sys, "stdout", buf):
        importlib.reload(log_mod)
        log_mod.get_logger("test").info("hello")
    out = buf.getvalue().strip()
    assert "INFO" in out and "test: hello" in out
