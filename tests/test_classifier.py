from unittest import mock
import importlib

from llm_gate import config
from llm_gate import classifier


def mock_llm_response(text: str):
    class Resp:
        def json(self):
            return {"response": text}

        def raise_for_status(self):
            pass

    return mock.patch("llm_gate.classifier.requests.post", return_value=Resp())


def test_classifier(tmp_path, monkeypatch):
    file = tmp_path / "config.yaml"
    file.write_text("critical_intents:\n  - buy\n")
    monkeypatch.setattr(config, "CONFIG_PATH", file)
    importlib.reload(config)
    importlib.reload(classifier)

    with mock_llm_response("intent=buy"):
        result = classifier.classify_request("I want to buy ETH")

    assert result["is_critical"] is True
    assert result["matched_intent"] == "buy"
