"""Safety and reserve management module.

Ensures the bot never endangers the account by:
- Tracking dynamic reserves
- Maintaining minimum XRP buffer
- Emergency shutdown when XRP gets critically low
- Trustline setup for new trading pairs
"""

import logging
from decimal import Decimal
from typing import Any

from xrpl.clients import JsonRpcClient
from xrpl.models import AccountLines, TrustSet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.transaction import submit_and_wait
from xrpl.wallet import Wallet

from bot.client import AccountBalance, get_account_balance
from bot.notifications import TelegramNotifier

logger = logging.getLogger(__name__)


def check_xrp_safety(
    balance: AccountBalance,
    config: dict[str, Any],
    notifier: TelegramNotifier,
) -> bool:
    """Check if we have enough XRP to continue trading safely.

    Args:
        balance: Current account balance snapshot.
        config: Full bot config.
        notifier: Telegram notifier for alerts.

    Returns:
        True if safe to continue, False if trading should stop.
    """
    safety_cfg = config.get("safety", {})
    emergency_threshold = Decimal(str(safety_cfg.get("emergency_xrp_threshold", 20)))
    min_buffer = Decimal(str(config.get("trading", {}).get("min_free_xrp_buffer", 50)))

    if balance.xrp_available < emergency_threshold:
        msg = (
            f"EMERGENCY: Available XRP ({balance.xrp_available:.2f}) "
            f"below emergency threshold ({emergency_threshold:.2f}). "
            f"Stopping all trading!"
        )
        logger.critical(msg)
        notifier.notify_emergency(msg)
        return False

    if balance.xrp_available < min_buffer:
        msg = (
            f"WARNING: Available XRP ({balance.xrp_available:.2f}) "
            f"below safety buffer ({min_buffer:.2f}). "
            f"Reducing trading activity."
        )
        logger.warning(msg)
        notifier.notify_error(msg)
        # Still allow trading but at reduced capacity
        return True

    return True


def compute_max_xrp_for_trading(
    balance: AccountBalance,
    config: dict[str, Any],
) -> Decimal:
    """Compute the maximum XRP we can allocate to trading grids.

    Respects both the allocation fraction and minimum buffer settings.

    Args:
        balance: Current account balance.
        config: Full bot config.

    Returns:
        Maximum XRP available for grid orders.
    """
    trading_cfg = config.get("trading", {})
    max_fraction = Decimal(str(trading_cfg.get("max_xrp_allocation_fraction", 0.6)))
    min_buffer = Decimal(str(trading_cfg.get("min_free_xrp_buffer", 50)))

    # Available after buffer
    after_buffer = max(Decimal("0"), balance.xrp_available - min_buffer)
    # Cap by fraction of total available
    by_fraction = balance.xrp_available * max_fraction

    result = min(after_buffer, by_fraction)
    logger.debug(
        "Max XRP for trading: %.2f (available=%.2f, buffer=%.2f, fraction=%.2f)",
        result, balance.xrp_available, min_buffer, max_fraction,
    )
    return result


def ensure_trustline(
    client: JsonRpcClient,
    wallet: Wallet,
    currency: str,
    issuer: str,
    limit: str = "1000000000",
) -> bool:
    """Ensure a trustline exists for a trading pair.

    Checks if trustline already exists. If not, creates one.
    Each trustline costs reserve_inc XRP in reserve (typically 0.2 XRP).

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        currency: Token currency code.
        issuer: Token issuer address.
        limit: Maximum trust limit.

    Returns:
        True if trustline exists or was created.
    """
    # Check existing trustlines
    try:
        resp = client.request(AccountLines(account=wallet.address, peer=issuer))
        for line in resp.result.get("lines", []):
            if line["currency"] == currency:
                logger.info("Trustline already exists for %s (%s)", currency, issuer)
                return True
    except Exception:
        logger.exception("Failed to check trustlines")
        return False

    # Create trustline
    logger.info("Creating trustline for %s (%s)", currency, issuer)
    tx = TrustSet(
        account=wallet.address,
        limit_amount=IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer,
            value=limit,
        ),
    )

    try:
        resp = submit_and_wait(tx, client, wallet)
        result = resp.result.get("meta", {}).get("TransactionResult", "")
        if result == "tesSUCCESS":
            logger.info("Trustline created for %s", currency)
            return True
        logger.warning("TrustSet failed: %s", result)
    except Exception:
        logger.exception("Exception creating trustline for %s", currency)
    return False


def reconcile_offers_with_ledger(
    ledger_offers: list[dict[str, Any]],
    state_offers: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[int]]:
    """Reconcile state-tracked offers with what's actually on the ledger.

    On restart, some offers may have been filled or expired while we were offline.
    This function identifies:
    - Offers that are still active on ledger (keep tracking)
    - Offers in state that are gone from ledger (potentially filled)

    Args:
        ledger_offers: Offers from AccountOffers for this pair.
        state_offers: Offers from our persisted state.

    Returns:
        Tuple of (still_active_state_offers, disappeared_sequences).
    """
    ledger_seqs = {o["seq"] for o in ledger_offers}
    still_active = []
    disappeared = []

    for so in state_offers:
        seq = so.get("sequence", 0)
        if seq in ledger_seqs:
            still_active.append(so)
        else:
            disappeared.append(seq)

    if disappeared:
        logger.info(
            "Reconciliation: %d offers disappeared from ledger (filled/expired): %s",
            len(disappeared),
            disappeared,
        )

    return still_active, disappeared
