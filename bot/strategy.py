"""Patient Grid Trading Strategy for XRPL DEX.

Core philosophy: patience over action. The bot places a grid of passive
limit orders around the current mid price. When a buy fills, it places
a corresponding sell at a higher price (capturing spread as profit).
When a sell fills, it places a new buy lower.

The grid only refreshes when the mid price drifts significantly.
All P&L is measured in XRP -- tokens are only vehicles, never the goal.
"""

import logging
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet

from bot.client import get_account_balance, get_token_balance
from bot.market import OrderbookSnapshot, fetch_orderbook
from bot.notifications import TelegramNotifier
from bot.orders import (
    PlacedOffer,
    cancel_all_pair_offers,
    classify_offer,
    get_our_offers,
    place_buy_offer,
    place_sell_offer,
)
from bot.safety import (
    check_xrp_safety,
    compute_max_xrp_for_trading,
    reconcile_offers_with_ledger,
)
from bot.state import BotState, PairState, get_pair_state, update_pair_state

logger = logging.getLogger(__name__)


@dataclass
class GridLevel:
    """A single level in our grid."""

    price: Decimal      # XRP per token
    xrp_amount: Decimal
    token_amount: Decimal
    side: str           # "buy" or "sell"


@dataclass
class PairContext:
    """Runtime context for one trading pair during a strategy cycle."""

    currency: str
    issuer: str
    grid_config: dict[str, Any]
    pair_state: PairState
    orderbook: OrderbookSnapshot | None = None
    token_balance: Decimal = Decimal("0")
    our_buy_offers: list[dict[str, Any]] = field(default_factory=list)
    our_sell_offers: list[dict[str, Any]] = field(default_factory=list)


def compute_grid_levels(
    mid_price: Decimal,
    grid_config: dict[str, Any],
) -> list[GridLevel]:
    """Compute the ideal grid levels around the mid price.

    Buy levels are placed below mid price, sell levels above.
    Spacing is multiplicative (each level is level_spacing further out).

    Args:
        mid_price: Current mid price (XRP per token).
        grid_config: Grid parameters from config.

    Returns:
        List of GridLevel objects.
    """
    buy_levels_count = grid_config.get("buy_levels", 3)
    sell_levels_count = grid_config.get("sell_levels", 3)
    spacing = Decimal(str(grid_config.get("level_spacing", 0.02)))
    order_size_xrp = Decimal(str(grid_config.get("order_size_xrp", 20)))
    min_spread = Decimal(str(grid_config.get("min_spread", 0.005)))

    levels: list[GridLevel] = []

    # Buy levels: below mid price
    for i in range(1, buy_levels_count + 1):
        offset = min_spread + spacing * i
        price = mid_price * (1 - offset)
        if price <= 0:
            continue
        token_amount = (order_size_xrp / price).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        levels.append(GridLevel(
            price=price,
            xrp_amount=order_size_xrp,
            token_amount=token_amount,
            side="buy",
        ))

    # Sell levels: above mid price
    for i in range(1, sell_levels_count + 1):
        offset = min_spread + spacing * i
        price = mid_price * (1 + offset)
        token_amount = (order_size_xrp / price).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )
        levels.append(GridLevel(
            price=price,
            xrp_amount=order_size_xrp,
            token_amount=token_amount,
            side="sell",
        ))

    return levels


def should_refresh_grid(
    current_mid: Decimal,
    grid_mid: Decimal,
    drift_threshold: Decimal,
) -> bool:
    """Determine if the grid should be refreshed due to price drift.

    The grid stays in place unless price moves beyond the threshold.
    This is the "patient" part -- avoid unnecessary churn.

    Args:
        current_mid: Current orderbook mid price.
        grid_mid: Mid price when grid was last placed.
        drift_threshold: Fractional threshold for refresh.

    Returns:
        True if grid should be refreshed.
    """
    if grid_mid <= 0:
        return True  # No grid placed yet
    drift = abs(current_mid - grid_mid) / grid_mid
    return drift > drift_threshold


def detect_fills(
    pair_state: PairState,
    ledger_offers: list[dict[str, Any]],
    currency: str,
    issuer: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Detect which of our tracked offers have been filled.

    Compares persisted offers with current ledger state.
    An offer that's in our state but not on the ledger was either
    filled or expired. We track both cases.

    Args:
        pair_state: Persisted pair state.
        ledger_offers: Current offers on ledger for our account.
        currency: Token currency code.
        issuer: Token issuer address.

    Returns:
        Tuple of (filled_buys, filled_sells) - lists of state offer dicts.
    """
    # Filter ledger offers to this pair
    pair_ledger_seqs: set[int] = set()
    for offer in ledger_offers:
        side = classify_offer(offer, currency, issuer)
        if side is not None:
            pair_ledger_seqs.add(offer["seq"])

    filled_buys: list[dict[str, Any]] = []
    filled_sells: list[dict[str, Any]] = []

    for offer in pair_state.active_buy_offers:
        seq = offer.get("sequence", 0)
        if seq not in pair_ledger_seqs:
            filled_buys.append(offer)

    for offer in pair_state.active_sell_offers:
        seq = offer.get("sequence", 0)
        if seq not in pair_ledger_seqs:
            filled_sells.append(offer)

    return filled_buys, filled_sells


def update_pnl_from_fills(
    pair_state: PairState,
    filled_buys: list[dict[str, Any]],
    filled_sells: list[dict[str, Any]],
    notifier: TelegramNotifier,
) -> PairState:
    """Update P&L tracking based on detected fills.

    When a buy fills: we now hold more tokens (inventory increases).
    When a sell fills: we've converted tokens back to XRP (potential profit).

    P&L is tracked in XRP. Profit = sell_xrp - (tokens_sold * avg_buy_price).

    Args:
        pair_state: Current pair state.
        filled_buys: List of buy offers that were filled.
        filled_sells: List of sell offers that were filled.
        notifier: Telegram notifier.

    Returns:
        Updated pair state.
    """
    inventory = Decimal(pair_state.token_inventory)
    avg_price = Decimal(pair_state.avg_buy_price)
    total_profit = Decimal(pair_state.total_xrp_profit)

    for buy in filled_buys:
        token_amt = Decimal(str(buy.get("token_amount", "0")))
        xrp_amt = Decimal(str(buy.get("xrp_amount", "0")))
        price = Decimal(str(buy.get("price", "0")))

        if token_amt > 0:
            # Update weighted average buy price
            total_cost = (inventory * avg_price) + xrp_amt
            inventory += token_amt
            avg_price = total_cost / inventory if inventory > 0 else Decimal("0")

        pair_state.total_buys += 1
        logger.info(
            "BUY filled: %.8f %s @ %.6f XRP/%s (%.6f XRP)",
            token_amt, pair_state.currency, price, pair_state.currency, xrp_amt,
        )
        notifier.notify_trade(
            pair_state.currency, "BUY",
            str(xrp_amt), str(token_amt), str(price),
        )

    for sell in filled_sells:
        token_amt = Decimal(str(sell.get("token_amount", "0")))
        xrp_amt = Decimal(str(sell.get("xrp_amount", "0")))
        price = Decimal(str(sell.get("price", "0")))

        if token_amt > 0 and avg_price > 0:
            cost_basis = token_amt * avg_price
            profit = xrp_amt - cost_basis
            total_profit += profit
            inventory = max(Decimal("0"), inventory - token_amt)
            logger.info(
                "SELL filled: %.8f %s @ %.6f XRP/%s (%.6f XRP, profit=%.6f XRP)",
                token_amt, pair_state.currency, price, pair_state.currency,
                xrp_amt, profit,
            )
        else:
            logger.info(
                "SELL filled: %.8f %s @ %.6f XRP/%s (%.6f XRP)",
                token_amt, pair_state.currency, price, pair_state.currency, xrp_amt,
            )

        pair_state.total_sells += 1
        notifier.notify_trade(
            pair_state.currency, "SELL",
            str(xrp_amt), str(token_amt), str(price),
        )

    pair_state.token_inventory = str(inventory)
    pair_state.avg_buy_price = str(avg_price)
    pair_state.total_xrp_profit = str(total_profit)

    return pair_state


def place_grid(
    client: JsonRpcClient,
    wallet: Wallet,
    ctx: PairContext,
    max_xrp_per_pair: Decimal,
) -> PairState:
    """Place a new grid of buy and sell orders for one pair.

    Cancels existing offers first, then places new ones at computed levels.
    Respects XRP budget constraints.

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        ctx: Pair context with orderbook and config.
        max_xrp_per_pair: Maximum XRP to allocate to this pair's buy orders.

    Returns:
        Updated pair state with new offers.
    """
    pair_state = ctx.pair_state
    ob = ctx.orderbook

    if ob is None or not ob.has_liquidity:
        logger.warning("No liquidity for %s, skipping grid placement", ctx.currency)
        return pair_state

    mid_price = ob.mid_price
    grid_config = ctx.grid_config
    expiration = grid_config.get("offer_expiration_seconds", 3600)

    # Cancel existing offers for this pair
    cancel_all_pair_offers(client, wallet, ctx.currency, ctx.issuer)

    # Compute grid levels
    levels = compute_grid_levels(mid_price, grid_config)

    # Place buy orders (limited by XRP budget)
    xrp_committed = Decimal("0")
    new_buys: list[dict[str, Any]] = []
    new_sells: list[dict[str, Any]] = []

    buy_levels = [l for l in levels if l.side == "buy"]
    sell_levels = [l for l in levels if l.side == "sell"]

    for level in buy_levels:
        if xrp_committed + level.xrp_amount > max_xrp_per_pair:
            logger.info(
                "XRP budget exhausted for %s buys (committed=%.2f, max=%.2f)",
                ctx.currency, xrp_committed, max_xrp_per_pair,
            )
            break

        result = place_buy_offer(
            client, wallet,
            ctx.currency, ctx.issuer,
            level.xrp_amount, level.token_amount,
            expiration,
        )
        if result:
            xrp_committed += level.xrp_amount
            new_buys.append({
                "sequence": result.sequence,
                "price": str(result.price),
                "xrp_amount": str(result.xrp_amount),
                "token_amount": str(result.token_amount),
            })

    # Place sell orders (limited by token inventory)
    token_available = ctx.token_balance
    min_profit_frac = Decimal(str(grid_config.get("min_profit_fraction", 0.003)))
    avg_buy = Decimal(pair_state.avg_buy_price)

    for level in sell_levels:
        # Only sell if we have tokens AND the sell price gives us profit
        if token_available <= 0:
            logger.debug("No token inventory for %s sells", ctx.currency)
            break

        if avg_buy > 0:
            profit_frac = (level.price - avg_buy) / avg_buy
            if profit_frac < min_profit_frac:
                logger.debug(
                    "Sell level at %.6f too close to avg buy %.6f (profit=%.4f%% < %.4f%%)",
                    level.price, avg_buy, float(profit_frac * 100),
                    float(min_profit_frac * 100),
                )
                continue

        sell_token_amount = min(level.token_amount, token_available)
        sell_xrp_amount = sell_token_amount * level.price

        result = place_sell_offer(
            client, wallet,
            ctx.currency, ctx.issuer,
            sell_xrp_amount, sell_token_amount,
            expiration,
        )
        if result:
            token_available -= sell_token_amount
            new_sells.append({
                "sequence": result.sequence,
                "price": str(result.price),
                "xrp_amount": str(result.xrp_amount),
                "token_amount": str(result.token_amount),
            })

    pair_state.active_buy_offers = new_buys
    pair_state.active_sell_offers = new_sells
    pair_state.grid_mid_price = str(mid_price)

    logger.info(
        "%s grid placed: %d buys, %d sells, mid=%.6f, xrp_committed=%.2f",
        ctx.currency, len(new_buys), len(new_sells), mid_price, xrp_committed,
    )

    return pair_state


def run_strategy_cycle(
    client: JsonRpcClient,
    wallet: Wallet,
    config: dict[str, Any],
    state: BotState,
    notifier: TelegramNotifier,
) -> BotState:
    """Execute one full strategy cycle across all trading pairs.

    Steps per pair:
    1. Fetch orderbook and compute mid price
    2. Check for filled offers and update P&L
    3. Decide whether to refresh the grid
    4. If refreshing, cancel old offers and place new grid

    The bot is PATIENT: it only refreshes when the price has drifted
    significantly or offers have been filled.

    Args:
        client: Connected XRPL client.
        wallet: Signing wallet.
        config: Full bot config.
        state: Current bot state.
        notifier: Telegram notifier.

    Returns:
        Updated bot state.
    """
    trading_cfg = config.get("trading", {})
    drift_threshold = Decimal(str(trading_cfg.get("price_drift_threshold", 0.01)))
    pairs = config.get("pairs", [])
    num_pairs = len(pairs)

    if num_pairs == 0:
        logger.warning("No trading pairs configured")
        return state

    # Get account balance and safety check
    balance = get_account_balance(client, wallet.address)
    if not check_xrp_safety(balance, config, notifier):
        # Emergency: cancel everything
        for pair_cfg in pairs:
            cancel_all_pair_offers(
                client, wallet,
                pair_cfg["currency"], pair_cfg["issuer"],
            )
        return state

    # Compute XRP budget per pair
    max_xrp_total = compute_max_xrp_for_trading(balance, config)
    max_xrp_per_pair = max_xrp_total / num_pairs

    # Get all our ledger offers once (shared across pairs)
    all_ledger_offers = get_our_offers(client, wallet.address)

    for pair_cfg in pairs:
        currency = pair_cfg["currency"]
        issuer = pair_cfg["issuer"]
        grid_config = pair_cfg.get("grid", {})

        logger.info("--- Processing pair: XRP/%s ---", currency)

        pair_state = get_pair_state(state, currency, issuer)

        # 1. Fetch orderbook
        orderbook = fetch_orderbook(client, currency, issuer)

        # 2. Get token balance
        token_balance = get_token_balance(client, wallet.address, currency, issuer)

        # 3. Filter ledger offers for this pair
        pair_ledger_buys = []
        pair_ledger_sells = []
        for offer in all_ledger_offers:
            side = classify_offer(offer, currency, issuer)
            if side == "buy":
                pair_ledger_buys.append(offer)
            elif side == "sell":
                pair_ledger_sells.append(offer)

        # 4. Detect fills
        filled_buys, filled_sells = detect_fills(
            pair_state, all_ledger_offers, currency, issuer,
        )

        has_fills = len(filled_buys) > 0 or len(filled_sells) > 0

        # 5. Update P&L from fills
        if has_fills:
            pair_state = update_pnl_from_fills(
                pair_state, filled_buys, filled_sells, notifier,
            )
            logger.info(
                "%s P&L: profit=%.6f XRP, inventory=%.8f %s, buys=%d, sells=%d",
                currency,
                Decimal(pair_state.total_xrp_profit),
                Decimal(pair_state.token_inventory),
                currency,
                pair_state.total_buys,
                pair_state.total_sells,
            )

        # 6. Remove filled offers from state tracking
        active_buy_seqs = {o["seq"] for o in pair_ledger_buys}
        active_sell_seqs = {o["seq"] for o in pair_ledger_sells}

        pair_state.active_buy_offers = [
            o for o in pair_state.active_buy_offers
            if o.get("sequence", 0) in active_buy_seqs
        ]
        pair_state.active_sell_offers = [
            o for o in pair_state.active_sell_offers
            if o.get("sequence", 0) in active_sell_seqs
        ]

        # 7. Decide if grid needs refresh
        grid_mid = Decimal(pair_state.grid_mid_price)
        needs_refresh = False

        if not orderbook.has_liquidity:
            logger.warning("No liquidity for %s, skipping", currency)
            update_pair_state(state, pair_state)
            continue

        if should_refresh_grid(orderbook.mid_price, grid_mid, drift_threshold):
            logger.info(
                "%s: price drifted (current=%.6f, grid=%.6f, threshold=%.4f%%)",
                currency, orderbook.mid_price, grid_mid,
                float(drift_threshold * 100),
            )
            needs_refresh = True

        if has_fills:
            logger.info("%s: fills detected, refreshing grid", currency)
            needs_refresh = True

        # Check if we have no active offers
        if not pair_state.active_buy_offers and not pair_state.active_sell_offers:
            logger.info("%s: no active offers, placing grid", currency)
            needs_refresh = True

        # 8. Place or refresh grid
        if needs_refresh:
            ctx = PairContext(
                currency=currency,
                issuer=issuer,
                grid_config=grid_config,
                pair_state=pair_state,
                orderbook=orderbook,
                token_balance=token_balance,
            )
            pair_state = place_grid(client, wallet, ctx, max_xrp_per_pair)
        else:
            logger.info(
                "%s: grid stable (mid=%.6f, %d buys, %d sells active)",
                currency, grid_mid,
                len(pair_state.active_buy_offers),
                len(pair_state.active_sell_offers),
            )

        update_pair_state(state, pair_state)

    return state
