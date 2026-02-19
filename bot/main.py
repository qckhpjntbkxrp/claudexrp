"""Main entry point for the XRPL DEX Trading Bot.

Initializes all components, runs the main trading loop,
and handles graceful shutdown.
"""

import logging
import os
import signal
import sys
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from bot.client import create_client, get_account_balance, load_wallet
from bot.notifications import TelegramNotifier
from bot.safety import ensure_trustline
from bot.state import BotState, load_state, save_state
from bot.strategy import run_strategy_cycle
from bot.utils import format_xrp

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
_shutdown_requested = False


def _handle_signal(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    logger.info("Shutdown signal received (%d), finishing current cycle...", signum)
    _shutdown_requested = True


def setup_logging(log_to_file: bool = True) -> None:
    """Configure logging with timestamps and levels.

    Logs to both stdout and a rotating file for mainnet auditability.

    Args:
        log_to_file: Whether to also log to bot.log file.
    """
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]

    if log_to_file:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            "bot.log", maxBytes=10 * 1024 * 1024, backupCount=5,
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    # Reduce noise from urllib3
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("xrpl").setLevel(logging.WARNING)


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """Load bot configuration from YAML file.

    Args:
        config_path: Path to config file.

    Returns:
        Config dict.
    """
    path = Path(config_path)
    if not path.exists():
        logger.error("Config file not found: %s", config_path)
        sys.exit(1)

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    logger.info("Config loaded from %s", config_path)
    logger.info("Network mode: %s", config["network"]["mode"])
    logger.info("Trading pairs: %d", len(config.get("pairs", [])))
    return config


def initialize_bot(config: dict[str, Any]) -> tuple:
    """Initialize all bot components.

    Args:
        config: Full bot config.

    Returns:
        Tuple of (client, wallet, state, notifier).
    """
    # Create XRPL client
    client = create_client(config)

    # Validate connection by querying server info
    try:
        from xrpl.models import ServerInfo
        resp = client.request(ServerInfo())
        server_state = resp.result.get("info", {}).get("server_state", "unknown")
        ledger_seq = resp.result.get("info", {}).get("validated_ledger", {}).get("seq", 0)
        logger.info("XRPL node connected: state=%s, ledger=%d", server_state, ledger_seq)
        if server_state not in ("full", "proposing", "validating"):
            logger.warning("Server state '%s' may not be fully synced!", server_state)
    except Exception:
        logger.exception("Failed to connect to XRPL node - check URL and network")
        raise

    # Load or create wallet
    wallet = load_wallet(config, client)

    # Load persisted state
    state_path = config.get("state", {}).get("file_path", "bot_state.json")
    state = load_state(state_path)

    # Create notifier
    notifier = TelegramNotifier(config)

    # Get initial balance
    balance = get_account_balance(client, wallet.address)
    logger.info(
        "Account: %s | XRP total: %s | Available: %s | Reserve: %s | OwnerCount: %d",
        wallet.address,
        format_xrp(balance.xrp_total),
        format_xrp(balance.xrp_available),
        format_xrp(balance.reserve_total),
        balance.owner_count,
    )

    # Record initial balance if first run
    if state.start_time == 0:
        state.initial_xrp_balance = str(balance.xrp_total)
        state.start_time = time.time()
        logger.info("First run - initial XRP balance: %s", format_xrp(balance.xrp_total))

    # Ensure trustlines for all trading pairs
    for pair_cfg in config.get("pairs", []):
        currency = pair_cfg["currency"]
        issuer = pair_cfg["issuer"]
        success = ensure_trustline(client, wallet, currency, issuer)
        if not success:
            logger.error("Failed to establish trustline for %s (%s)", currency, issuer)
            notifier.notify_error(f"Failed to create trustline for {currency}")

    return client, wallet, state, notifier


def log_pnl_summary(state: BotState, current_xrp: Decimal) -> None:
    """Log a P&L summary across all pairs.

    Args:
        state: Current bot state.
        current_xrp: Current total XRP balance.
    """
    initial = Decimal(state.initial_xrp_balance)
    net_change = current_xrp - initial
    pct_change = (net_change / initial * 100) if initial > 0 else Decimal("0")

    logger.info("=== P&L Summary ===")
    logger.info("Initial XRP:  %s", format_xrp(initial))
    logger.info("Current XRP:  %s", format_xrp(current_xrp))
    logger.info("Net change:   %s XRP (%+.4f%%)", format_xrp(net_change), pct_change)

    for key, pair_data in state.pairs.items():
        profit = Decimal(pair_data.get("total_xrp_profit", "0"))
        inventory = Decimal(pair_data.get("token_inventory", "0"))
        buys = pair_data.get("total_buys", 0)
        sells = pair_data.get("total_sells", 0)
        currency = pair_data.get("currency", key)
        logger.info(
            "  %s: profit=%s XRP, inventory=%s, buys=%d, sells=%d",
            currency, format_xrp(profit), inventory, buys, sells,
        )


def run_bot(config_path: str = "config.yaml") -> None:
    """Main bot entry point. Runs the trading loop until shutdown.

    Args:
        config_path: Path to YAML config file.
    """
    global _shutdown_requested

    setup_logging()
    load_dotenv()  # Load .env file

    logger.info("XRPL DEX Trading Bot starting...")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Load config
    config = load_config(config_path)

    # Initialize components
    client, wallet, state, notifier = initialize_bot(config)

    state_path = config.get("state", {}).get("file_path", "bot_state.json")
    loop_interval = config.get("trading", {}).get("loop_interval_seconds", 30)
    safety_cfg = config.get("safety", {})
    max_errors = safety_cfg.get("max_consecutive_errors", 5)
    error_pause = safety_cfg.get("error_pause_seconds", 300)

    consecutive_errors = 0

    notifier.notify_status(
        f"Bot started on {config['network']['mode']}\n"
        f"Wallet: `{wallet.address}`\n"
        f"Pairs: {len(config.get('pairs', []))}"
    )

    logger.info("Entering main trading loop (interval=%ds)", loop_interval)

    while not _shutdown_requested:
        try:
            # Run one strategy cycle
            state = run_strategy_cycle(client, wallet, config, state, notifier)

            # Save state after each cycle
            save_state(state, state_path)

            # Log P&L periodically
            balance = get_account_balance(client, wallet.address)
            log_pnl_summary(state, balance.xrp_total)

            # Reset error counter on success
            consecutive_errors = 0

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt, shutting down...")
            break

        except Exception:
            consecutive_errors += 1
            logger.exception(
                "Error in trading cycle (%d/%d consecutive)",
                consecutive_errors, max_errors,
            )

            if consecutive_errors >= max_errors:
                msg = (
                    f"Too many consecutive errors ({consecutive_errors}). "
                    f"Pausing for {error_pause}s."
                )
                logger.error(msg)
                notifier.notify_error(msg)
                time.sleep(error_pause)
                consecutive_errors = 0
                continue

        # Wait for next cycle
        if not _shutdown_requested:
            logger.debug("Sleeping %ds until next cycle...", loop_interval)
            # Sleep in small increments to allow fast shutdown
            for _ in range(loop_interval):
                if _shutdown_requested:
                    break
                time.sleep(1)

    # Graceful shutdown
    logger.info("Shutting down gracefully...")
    save_state(state, state_path)
    notifier.notify_status("Bot stopped gracefully.")
    logger.info("Bot stopped.")


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    run_bot(config_file)
