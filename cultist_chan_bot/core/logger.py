"""Logging utilities."""

from __future__ import annotations

import logging
import sys

from .config import load_config

_CONFIGURED = False


def _setup() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    cfg = load_config()
    level = getattr(logging, getattr(cfg, "LOG_LEVEL", "INFO").upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return configured logger."""
    _setup()
    return logging.getLogger(name)

