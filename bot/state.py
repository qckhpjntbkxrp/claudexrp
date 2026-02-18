"""State persistence module.

Saves and loads bot state to/from JSON file so the bot survives restarts.
Tracks per-pair grid state, P&L, and offer history.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


@dataclass
class PairState:
    """Persisted state for one trading pair."""

    currency: str
    issuer: str
    # Grid reference price when grid was last placed
    grid_mid_price: str = "0"
    # Our active offer sequences on the ledger
    active_buy_offers: list[dict[str, Any]] = field(default_factory=list)
    active_sell_offers: list[dict[str, Any]] = field(default_factory=list)
    # P&L tracking: XRP gained from completed round-trips
    total_xrp_profit: str = "0"
    # Number of completed buy fills
    total_buys: int = 0
    # Number of completed sell fills
    total_sells: int = 0
    # Token inventory currently held (bought but not yet sold back)
    token_inventory: str = "0"
    # Average buy price of current inventory (XRP per token)
    avg_buy_price: str = "0"


@dataclass
class BotState:
    """Full bot state."""

    # XRP balance when bot first started
    initial_xrp_balance: str = "0"
    # Timestamp of first start
    start_time: float = 0.0
    # Per-pair states keyed by "currency:issuer"
    pairs: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Last update timestamp
    last_update: float = 0.0


def _pair_key(currency: str, issuer: str) -> str:
    """Generate a unique key for a trading pair."""
    return f"{currency}:{issuer}"


def load_state(file_path: str) -> BotState:
    """Load bot state from JSON file.

    Args:
        file_path: Path to state file.

    Returns:
        BotState instance (empty if file doesn't exist).
    """
    if not os.path.exists(file_path):
        logger.info("No state file found at %s, starting fresh", file_path)
        return BotState()

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        state = BotState(
            initial_xrp_balance=data.get("initial_xrp_balance", "0"),
            start_time=data.get("start_time", 0.0),
            pairs=data.get("pairs", {}),
            last_update=data.get("last_update", 0.0),
        )
        logger.info("State loaded from %s (%d pairs)", file_path, len(state.pairs))
        return state
    except (json.JSONDecodeError, KeyError):
        logger.exception("Failed to parse state file %s, starting fresh", file_path)
        return BotState()


def save_state(state: BotState, file_path: str) -> None:
    """Save bot state to JSON file atomically.

    Writes to a temp file first then renames to avoid corruption.

    Args:
        state: Current bot state.
        file_path: Path to state file.
    """
    state.last_update = time.time()
    tmp_path = file_path + ".tmp"
    try:
        with open(tmp_path, "w") as f:
            json.dump(asdict(state), f, cls=DecimalEncoder, indent=2)
        os.replace(tmp_path, file_path)
        logger.debug("State saved to %s", file_path)
    except OSError:
        logger.exception("Failed to save state to %s", file_path)


def get_pair_state(state: BotState, currency: str, issuer: str) -> PairState:
    """Get or create state for a specific trading pair.

    Args:
        state: Current bot state.
        currency: Token currency code.
        issuer: Token issuer address.

    Returns:
        PairState for this pair.
    """
    key = _pair_key(currency, issuer)
    if key not in state.pairs:
        ps = PairState(currency=currency, issuer=issuer)
        state.pairs[key] = asdict(ps)
    data = state.pairs[key]
    return PairState(**data)


def update_pair_state(state: BotState, pair_state: PairState) -> None:
    """Write pair state back into the main bot state.

    Args:
        state: Current bot state.
        pair_state: Updated pair state to persist.
    """
    key = _pair_key(pair_state.currency, pair_state.issuer)
    state.pairs[key] = asdict(pair_state)
