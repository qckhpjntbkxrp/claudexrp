"""Telegram notification module.

Sends alerts for trades, errors, and status updates.
Uses the Telegram Bot API via simple HTTP requests.
"""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send messages via Telegram Bot API."""

    def __init__(self, config: dict[str, Any]) -> None:
        tg_cfg = config.get("telegram", {})
        self.enabled: bool = tg_cfg.get("enabled", False)
        self.token: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id: str = os.environ.get("TELEGRAM_CHAT_ID", "")

        if self.enabled and (not self.token or not self.chat_id):
            logger.warning(
                "Telegram enabled but TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. "
                "Disabling notifications."
            )
            self.enabled = False

    def send(self, message: str) -> bool:
        """Send a text message via Telegram.

        Args:
            message: Text to send (supports Markdown).

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return True
            logger.warning("Telegram API returned %d: %s", resp.status_code, resp.text)
        except requests.RequestException:
            logger.exception("Failed to send Telegram message")
        return False

    def notify_trade(self, pair: str, side: str, xrp_amount: str, token_amount: str, price: str) -> None:
        """Notify about a completed trade."""
        self.send(
            f"*Trade Executed*\n"
            f"Pair: XRP/{pair}\n"
            f"Side: {side}\n"
            f"XRP: {xrp_amount}\n"
            f"Token: {token_amount}\n"
            f"Price: {price}"
        )

    def notify_error(self, error: str) -> None:
        """Notify about a critical error."""
        self.send(f"*Bot Error*\n{error}")

    def notify_status(self, message: str) -> None:
        """Send a status update."""
        self.send(f"*Status*\n{message}")

    def notify_emergency(self, message: str) -> None:
        """Send an emergency alert."""
        self.send(f"*EMERGENCY*\n{message}")
