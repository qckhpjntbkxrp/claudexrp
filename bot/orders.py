"""Order management module for XRPL DEX.

Handles creating, cancelling, and tracking offers on the XRPL ledger.
All offers use tfPassive flag and Expiration for safety.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from xrpl.clients import JsonRpcClient
from xrpl.models import AccountOffers, OfferCancel, OfferCreate
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.transaction import submit_and_wait
from xrpl.wallet import Wallet

from bot.utils import ripple_expiration, xrp_to_drops

logger = logging.getLogger(__name__)

# tfPassive: offer won't immediately cross existing offers
TF_PASSIVE: int = 65536


@dataclass
class PlacedOffer:
    """Record of an offer we placed on the ledger."""

    sequence: int           # Offer sequence (for cancel/replace)
    side: str               # "buy" or "sell"
    price: Decimal          # XRP per token
    xrp_amount: Decimal     # XRP amount
    token_amount: Decimal   # Token amount
    currency: str
    issuer: str


def get_our_offers(
    client: JsonRpcClient,
    address: str,
) -> list[dict[str, Any]]:
    """Fetch all active offers for our account from the ledger.

    This is the source of truth. State file offers must be reconciled
    with ledger offers on every restart.

    Args:
        client: Connected XRPL client.
        address: Our account address.

    Returns:
        List of offer dicts from AccountOffers response.
    """
    all_offers: list[dict[str, Any]] = []
    marker = None

    while True:
        kwargs: dict[str, Any] = {"account": address}
        if marker is not None:
            kwargs["marker"] = marker
        resp = client.request(AccountOffers(**kwargs))
        offers = resp.result.get("offers", [])
        all_offers.extend(offers)
        marker = resp.result.get("marker")
        if marker is None:
            break

    logger.debug("Found %d active offers on ledger for %s", len(all_offers), address)
    return all_offers


def classify_offer(
    offer: dict[str, Any],
    currency: str,
    issuer: str,
) -> str | None:
    """Classify a ledger offer as 'buy' or 'sell' for a given pair.

    Buy: we pay XRP (taker_gets=XRP), we get token (taker_pays=token)
    Wait -- from AccountOffers perspective:
      - taker_gets = what the taker gets = what WE are offering
      - taker_pays = what the taker pays = what WE want

    So for a BUY (we buy token with XRP):
      - taker_gets = XRP (we offer XRP)
      - taker_pays = token (we want token)

    For a SELL (we sell token for XRP):
      - taker_gets = token (we offer token)
      - taker_pays = XRP (we want XRP)

    Args:
        offer: Offer dict from AccountOffers.
        currency: Token currency code.
        issuer: Token issuer address.

    Returns:
        "buy", "sell", or None if offer doesn't match this pair.
    """
    tg = offer.get("taker_gets", "")
    tp = offer.get("taker_pays", "")

    # Buy: taker_gets is XRP string (drops), taker_pays is token dict
    if isinstance(tg, str) and isinstance(tp, dict):
        if tp.get("currency") == currency and tp.get("issuer") == issuer:
            return "buy"

    # Sell: taker_gets is token dict, taker_pays is XRP string (drops)
    if isinstance(tg, dict) and isinstance(tp, str):
        if tg.get("currency") == currency and tg.get("issuer") == issuer:
            return "sell"

    return None


def place_buy_offer(
    client: JsonRpcClient,
    wallet: Wallet,
    currency: str,
    issuer: str,
    xrp_amount: Decimal,
    token_amount: Decimal,
    expiration_seconds: int,
) -> PlacedOffer | None:
    """Place a passive buy offer: pay XRP, receive token.

    Uses tfPassive so the offer sits on the book and waits to be taken,
    rather than immediately crossing existing offers.

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        currency: Token currency code.
        issuer: Token issuer address.
        xrp_amount: XRP to pay.
        token_amount: Token amount to receive.
        expiration_seconds: Offer TTL in seconds.

    Returns:
        PlacedOffer on success, None on failure.
    """
    price = xrp_amount / token_amount if token_amount > 0 else Decimal("0")
    logger.info(
        "Placing BUY: %.6f XRP for %.8f %s @ %.6f XRP/%s",
        xrp_amount, token_amount, currency, price, currency,
    )

    tx = OfferCreate(
        account=wallet.address,
        taker_gets=IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer,
            value=str(token_amount),
        ),
        taker_pays=xrp_to_drops(xrp_amount),
        flags=TF_PASSIVE,
        expiration=ripple_expiration(expiration_seconds),
    )

    try:
        resp = submit_and_wait(tx, client, wallet)
        result = resp.result.get("meta", {}).get("TransactionResult", "")
        if result == "tesSUCCESS":
            seq = resp.result.get("Sequence", 0)
            # Get the actual offer sequence from the created offer node
            offer_seq = _extract_offer_sequence(resp.result)
            if offer_seq is None:
                offer_seq = seq
            logger.info("BUY offer placed, sequence=%d", offer_seq)
            return PlacedOffer(
                sequence=offer_seq,
                side="buy",
                price=price,
                xrp_amount=xrp_amount,
                token_amount=token_amount,
                currency=currency,
                issuer=issuer,
            )
        logger.warning("BUY offer failed: %s", result)
    except Exception:
        logger.exception("Exception placing BUY offer")
    return None


def place_sell_offer(
    client: JsonRpcClient,
    wallet: Wallet,
    currency: str,
    issuer: str,
    xrp_amount: Decimal,
    token_amount: Decimal,
    expiration_seconds: int,
) -> PlacedOffer | None:
    """Place a passive sell offer: pay token, receive XRP.

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        currency: Token currency code.
        issuer: Token issuer address.
        xrp_amount: XRP to receive.
        token_amount: Token amount to pay.
        expiration_seconds: Offer TTL in seconds.

    Returns:
        PlacedOffer on success, None on failure.
    """
    price = xrp_amount / token_amount if token_amount > 0 else Decimal("0")
    logger.info(
        "Placing SELL: %.8f %s for %.6f XRP @ %.6f XRP/%s",
        token_amount, currency, xrp_amount, price, currency,
    )

    tx = OfferCreate(
        account=wallet.address,
        taker_gets=xrp_to_drops(xrp_amount),
        taker_pays=IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer,
            value=str(token_amount),
        ),
        flags=TF_PASSIVE,
        expiration=ripple_expiration(expiration_seconds),
    )

    try:
        resp = submit_and_wait(tx, client, wallet)
        result = resp.result.get("meta", {}).get("TransactionResult", "")
        if result == "tesSUCCESS":
            seq = resp.result.get("Sequence", 0)
            offer_seq = _extract_offer_sequence(resp.result)
            if offer_seq is None:
                offer_seq = seq
            logger.info("SELL offer placed, sequence=%d", offer_seq)
            return PlacedOffer(
                sequence=offer_seq,
                side="sell",
                price=price,
                xrp_amount=xrp_amount,
                token_amount=token_amount,
                currency=currency,
                issuer=issuer,
            )
        logger.warning("SELL offer failed: %s", result)
    except Exception:
        logger.exception("Exception placing SELL offer")
    return None


def cancel_offer(
    client: JsonRpcClient,
    wallet: Wallet,
    offer_sequence: int,
) -> bool:
    """Cancel an existing offer by its sequence number.

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        offer_sequence: The sequence number of the offer to cancel.

    Returns:
        True if cancelled successfully.
    """
    logger.info("Cancelling offer sequence=%d", offer_sequence)
    tx = OfferCancel(
        account=wallet.address,
        offer_sequence=offer_sequence,
    )

    try:
        resp = submit_and_wait(tx, client, wallet)
        result = resp.result.get("meta", {}).get("TransactionResult", "")
        if result == "tesSUCCESS":
            logger.info("Offer %d cancelled", offer_sequence)
            return True
        logger.warning("Cancel offer %d failed: %s", offer_sequence, result)
    except Exception:
        logger.exception("Exception cancelling offer %d", offer_sequence)
    return False


def cancel_all_pair_offers(
    client: JsonRpcClient,
    wallet: Wallet,
    currency: str,
    issuer: str,
) -> int:
    """Cancel all our offers for a specific trading pair.

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        currency: Token currency code.
        issuer: Token issuer address.

    Returns:
        Number of offers successfully cancelled.
    """
    our_offers = get_our_offers(client, wallet.address)
    cancelled = 0
    for offer in our_offers:
        side = classify_offer(offer, currency, issuer)
        if side is not None:
            if cancel_offer(client, wallet, offer["seq"]):
                cancelled += 1
    logger.info("Cancelled %d offers for %s", cancelled, currency)
    return cancelled


def _extract_offer_sequence(tx_result: dict[str, Any]) -> int | None:
    """Extract the offer sequence from a transaction result's metadata.

    Looks through AffectedNodes for the CreatedNode of type Offer.

    Args:
        tx_result: Transaction result dict.

    Returns:
        Offer sequence number or None if not found.
    """
    meta = tx_result.get("meta", {})
    if isinstance(meta, str):
        return None
    for node in meta.get("AffectedNodes", []):
        created = node.get("CreatedNode", {})
        if created.get("LedgerEntryType") == "Offer":
            new_fields = created.get("NewFields", {})
            return new_fields.get("Sequence")
    return None
