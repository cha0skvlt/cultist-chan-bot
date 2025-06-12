from llm_gate import config
import importlib


def test_config(tmp_path, monkeypatch):
    file = tmp_path / "config.yaml"
    file.write_text(
        """\ncritical_intents:\n  - buy\nallowlist_contracts:\n  - 0xABC123...\n"""
    )
    monkeypatch.setattr(config, "CONFIG_PATH", file)
    importlib.reload(config)
    assert config.is_critical_intent("buy")
    assert config.is_allowed_contract("0xABC123...")
    assert not config.is_critical_intent("chat")
