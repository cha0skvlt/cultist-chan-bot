"""NFT scanning integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List

from time import time
from .logger import get_logger
from threading import Timer

from .scanner import evaluate_nft
from .db import log_nft_purchase
from .persona import generate_persona_reply


DATA_FILE = Path(__file__).with_name("nfts.json")

SECONDS_PER_DAY = 24 * 60 * 60


def scan_nfts(loader: Callable[[], List[dict]] | None = None) -> list[dict]:
    """Return NFTs approved by TinyLlama."""
    if loader is None:
        if DATA_FILE.exists():
            nfts = json.loads(DATA_FILE.read_text())
        else:
            nfts = []
    else:
        nfts = loader()
    approved: list[dict] = []
    for nft in nfts:
        if evaluate_nft(nft):
            purchase_nft(nft)
            approved.append(nft)
    return approved


def purchase_nft(nft: dict) -> str:
    """Simulate purchasing an NFT and log the result."""
    log_nft_purchase(nft, "success", time())
    return generate_persona_reply("nft_purchase", {"nft": nft})


def run_daily_nft_scan() -> None:
    """Run NFT scan once and log progress."""
    logger = get_logger(__name__)
    logger.info("NFT scan started")
    scan_nfts()
    logger.info("NFT scan finished")


def schedule_daily_nft_scan() -> None:
    """Schedule daily NFT scanning loop."""

    def _run() -> None:
        run_daily_nft_scan()
        Timer(SECONDS_PER_DAY, _run).start()

    Timer(0, _run).start()
