"""Orderbook analysis and market data for XRPL DEX.

Fetches bid/ask orderbooks, computes mid price and spread
for XRP vs issued token pairs.
"""

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from xrpl.clients import JsonRpcClient
from xrpl.models import AMMInfo, BookOffers
from xrpl.models.currencies import IssuedCurrency, XRP

logger = logging.getLogger(__name__)


@dataclass
class OrderbookLevel:
    """A single price level in the orderbook."""

    price: Decimal           # Price in XRP per token
    amount_xrp: Decimal      # XRP amount at this level
    amount_token: Decimal    # Token amount at this level
    owner: str               # Account that placed the offer
    sequence: int            # Offer sequence number


@dataclass
class OrderbookSnapshot:
    """Complete orderbook snapshot for one trading pair."""

    currency: str
    issuer: str
    bids: list[OrderbookLevel] = field(default_factory=list)  # Sorted best-first (highest price)
    asks: list[OrderbookLevel] = field(default_factory=list)  # Sorted best-first (lowest price)
    best_bid: Decimal = Decimal("0")
    best_ask: Decimal = Decimal("0")
    mid_price: Decimal = Decimal("0")
    spread_fraction: Decimal = Decimal("0")
    has_liquidity: bool = False


def _parse_amount_xrp(amount: str | dict) -> Decimal:
    """Parse an amount field that represents XRP (as drops string)."""
    if isinstance(amount, str):
        return Decimal(amount) / Decimal("1000000")
    return Decimal("0")


def _parse_amount_token(amount: str | dict) -> Decimal:
    """Parse an amount field that represents an issued token."""
    if isinstance(amount, dict):
        return Decimal(amount.get("value", "0"))
    return Decimal("0")


def fetch_orderbook(
    client: JsonRpcClient,
    currency: str,
    issuer: str,
    limit: int = 20,
) -> OrderbookSnapshot:
    """Fetch both sides of the orderbook for an XRP/token pair.

    Asks: offers selling token for XRP (we buy token with XRP).
    Bids: offers buying token with XRP (we sell token for XRP).

    The price is always expressed as XRP per token.

    Args:
        client: Connected XRPL client.
        currency: Token currency code.
        issuer: Token issuer address.
        limit: Max offers per side.

    Returns:
        OrderbookSnapshot with parsed levels and computed mid/spread.
    """
    token = IssuedCurrency(currency=currency, issuer=issuer)
    snap = OrderbookSnapshot(currency=currency, issuer=issuer)

    # --- Asks: someone is selling token, wanting XRP ---
    # taker_gets = token, taker_pays = XRP
    # From our perspective: we pay XRP, we get token => this is our buy side
    # price = XRP / token
    try:
        asks_resp = client.request(BookOffers(
            taker_gets=token,
            taker_pays=XRP(),
            limit=limit,
        ))
        for offer in asks_resp.result.get("offers", []):
            xrp_amount = _parse_amount_xrp(offer["TakerPays"])
            token_amount = _parse_amount_token(offer["TakerGets"])
            if token_amount > 0:
                price = xrp_amount / token_amount
                snap.asks.append(OrderbookLevel(
                    price=price,
                    amount_xrp=xrp_amount,
                    amount_token=token_amount,
                    owner=offer["Account"],
                    sequence=offer["Sequence"],
                ))
    except Exception:
        logger.exception("Failed to fetch asks for %s", currency)

    # --- Bids: someone is buying token, offering XRP ---
    # taker_gets = XRP, taker_pays = token
    # From our perspective: we get XRP, we pay token => this is our sell side
    # price = XRP / token
    try:
        bids_resp = client.request(BookOffers(
            taker_gets=XRP(),
            taker_pays=token,
            limit=limit,
        ))
        for offer in bids_resp.result.get("offers", []):
            xrp_amount = _parse_amount_xrp(offer["TakerGets"])
            token_amount = _parse_amount_token(offer["TakerPays"])
            if token_amount > 0:
                price = xrp_amount / token_amount
                snap.bids.append(OrderbookLevel(
                    price=price,
                    amount_xrp=xrp_amount,
                    amount_token=token_amount,
                    owner=offer["Account"],
                    sequence=offer["Sequence"],
                ))
    except Exception:
        logger.exception("Failed to fetch bids for %s", currency)

    # Sort: asks lowest-first, bids highest-first
    snap.asks.sort(key=lambda x: x.price)
    snap.bids.sort(key=lambda x: x.price, reverse=True)

    # Compute mid price and spread
    if snap.asks and snap.bids:
        snap.best_ask = snap.asks[0].price
        snap.best_bid = snap.bids[0].price
        if snap.best_ask > 0:
            snap.mid_price = (snap.best_bid + snap.best_ask) / 2
            snap.spread_fraction = (snap.best_ask - snap.best_bid) / snap.mid_price
            snap.has_liquidity = True

    logger.debug(
        "%s orderbook: bid=%s ask=%s mid=%s spread=%.4f%%",
        currency,
        snap.best_bid,
        snap.best_ask,
        snap.mid_price,
        float(snap.spread_fraction * 100),
    )
    return snap


def check_amm_liquidity(
    client: JsonRpcClient,
    currency: str,
    issuer: str,
) -> dict[str, Any] | None:
    """Check if an AMM pool exists for this pair and return its info.

    Args:
        client: Connected XRPL client.
        currency: Token currency code.
        issuer: Token issuer address.

    Returns:
        AMM info dict or None if no pool exists.
    """
    try:
        resp = client.request(AMMInfo(
            asset=XRP(),
            asset2=IssuedCurrency(currency=currency, issuer=issuer),
        ))
        amm = resp.result.get("amm")
        if amm:
            logger.info("AMM pool found for XRP/%s", currency)
            return amm
    except Exception:
        logger.debug("No AMM pool for XRP/%s (or query failed)", currency)
    return None
