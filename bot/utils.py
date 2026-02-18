"""Utility helpers for XRPL-specific conversions and common operations."""

import time
from decimal import Decimal, ROUND_DOWN

# XRPL epoch starts 2000-01-01T00:00:00Z, Unix epoch starts 1970-01-01T00:00:00Z.
RIPPLE_EPOCH_OFFSET: int = 946_684_800


def unix_to_ripple_time(unix_timestamp: int) -> int:
    """Convert Unix timestamp to Ripple epoch timestamp.

    The XRPL uses an epoch of 2000-01-01. Using the wrong epoch
    causes offers to expire immediately.
    """
    return unix_timestamp - RIPPLE_EPOCH_OFFSET


def ripple_time_now() -> int:
    """Current time in Ripple epoch seconds."""
    return unix_to_ripple_time(int(time.time()))


def ripple_expiration(seconds_from_now: int) -> int:
    """Compute an offer Expiration value N seconds in the future (Ripple epoch)."""
    return ripple_time_now() + seconds_from_now


def drops_to_xrp(drops: str | int) -> Decimal:
    """Convert drops (string or int) to XRP as Decimal."""
    return Decimal(str(drops)) / Decimal("1000000")


def xrp_to_drops(xrp: Decimal | float | str) -> str:
    """Convert XRP amount to drops string (no decimals)."""
    d = Decimal(str(xrp)) * Decimal("1000000")
    return str(d.quantize(Decimal("1"), rounding=ROUND_DOWN))


def format_xrp(xrp: Decimal | float | str) -> str:
    """Format XRP amount for display (6 decimal places)."""
    return f"{Decimal(str(xrp)):.6f}"


def format_token(amount: Decimal | float | str, currency: str) -> str:
    """Format token amount for display."""
    return f"{Decimal(str(amount)):.8f} {currency}"
