from __future__ import annotations

"""Config utilities for the gate."""

from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).with_name("config.yaml")
_CONFIG: dict | None = None


def load_config() -> dict:
    """Load YAML configuration."""
    global _CONFIG
    if _CONFIG is None:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open() as fh:
                _CONFIG = yaml.safe_load(fh) or {}
        else:
            _CONFIG = {}
    return _CONFIG


def reload_config() -> dict:
    """Reload configuration from disk."""
    global _CONFIG
    _CONFIG = None
    return load_config()


def is_critical_intent(intent: str) -> bool:
    cfg = load_config()
    return intent in cfg.get("critical_intents", [])


def is_allowed_contract(addr: str) -> bool:
    cfg = load_config()
    return addr in cfg.get("allowlist_contracts", [])
