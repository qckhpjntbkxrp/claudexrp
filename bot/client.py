"""XRPL client connection and wallet management.

Handles both testnet (faucet) and mainnet (secret from .env) modes.
Provides synchronous JSON-RPC client access and account info queries.
"""

import logging
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from xrpl.clients import JsonRpcClient
from xrpl.models import AccountInfo, AccountLines, ServerInfo
from xrpl.wallet import Wallet, generate_faucet_wallet

from bot.utils import drops_to_xrp

logger = logging.getLogger(__name__)


@dataclass
class AccountBalance:
    """Snapshot of an account's XRP balance and reserve info."""

    xrp_total: Decimal        # Total XRP in account
    owner_count: int           # Number of owned objects (affects reserve)
    reserve_base: Decimal      # Base reserve in XRP
    reserve_inc: Decimal       # Per-object reserve increment in XRP
    reserve_total: Decimal     # Total reserve (base + owner_count * inc)
    xrp_available: Decimal     # XRP available for trading (total - reserve)


def create_client(config: dict[str, Any]) -> JsonRpcClient:
    """Create an XRPL JsonRpcClient based on network config.

    Args:
        config: Full bot config dict with 'network' section.

    Returns:
        Connected JsonRpcClient instance.
    """
    net_cfg = config["network"]
    mode = net_cfg["mode"]
    if mode == "testnet":
        url = net_cfg["testnet_url"]
    elif mode == "mainnet":
        url = net_cfg["mainnet_url"]
    else:
        raise ValueError(f"Unknown network mode: {mode}")

    logger.info("Connecting to XRPL %s at %s", mode, url)
    return JsonRpcClient(url)


def load_wallet(config: dict[str, Any], client: JsonRpcClient) -> Wallet:
    """Load or create wallet depending on network mode.

    Testnet: generates a funded faucet wallet.
    Mainnet: loads from XRPL_SECRET environment variable.

    Args:
        config: Full bot config dict.
        client: Connected XRPL client.

    Returns:
        Wallet instance ready for signing.
    """
    mode = config["network"]["mode"]

    if mode == "testnet":
        logger.info("Generating testnet faucet wallet...")
        wallet = generate_faucet_wallet(client, debug=True)
        logger.info("Testnet wallet: %s", wallet.address)
        return wallet

    # Mainnet: load from env
    secret = os.environ.get("XRPL_SECRET")
    if not secret:
        raise RuntimeError("XRPL_SECRET environment variable not set for mainnet")

    wallet = Wallet.from_seed(secret)
    logger.info("Mainnet wallet loaded: %s", wallet.address)
    return wallet


def get_reserves(client: JsonRpcClient) -> tuple[Decimal, Decimal]:
    """Query current reserve requirements from the network.

    NEVER hardcode reserves - they can change via amendment votes.

    Returns:
        Tuple of (base_reserve_xrp, increment_reserve_xrp).
    """
    resp = client.request(ServerInfo())
    info = resp.result["info"]
    validated = info["validated_ledger"]
    base = Decimal(str(validated["reserve_base_xrp"]))
    inc = Decimal(str(validated["reserve_inc_xrp"]))
    return base, inc


def get_account_balance(client: JsonRpcClient, address: str) -> AccountBalance:
    """Get comprehensive account balance including dynamic reserves.

    Args:
        client: Connected XRPL client.
        address: XRPL account address.

    Returns:
        AccountBalance with all computed fields.
    """
    # Get account info
    resp = client.request(AccountInfo(account=address, ledger_index="validated"))
    acct = resp.result["account_data"]
    xrp_total = drops_to_xrp(acct["Balance"])
    owner_count = int(acct["OwnerCount"])

    # Get dynamic reserves
    reserve_base, reserve_inc = get_reserves(client)
    reserve_total = reserve_base + (reserve_inc * owner_count)
    xrp_available = max(Decimal("0"), xrp_total - reserve_total)

    return AccountBalance(
        xrp_total=xrp_total,
        owner_count=owner_count,
        reserve_base=reserve_base,
        reserve_inc=reserve_inc,
        reserve_total=reserve_total,
        xrp_available=xrp_available,
    )


def get_token_balance(
    client: JsonRpcClient,
    address: str,
    currency: str,
    issuer: str,
) -> Decimal:
    """Get balance of a specific issued token.

    Args:
        client: Connected XRPL client.
        address: XRPL account address.
        currency: Token currency code.
        issuer: Token issuer address.

    Returns:
        Token balance as Decimal (0 if no trustline).
    """
    resp = client.request(AccountLines(account=address, peer=issuer))
    for line in resp.result.get("lines", []):
        if line["currency"] == currency:
            return Decimal(line["balance"])
    return Decimal("0")
