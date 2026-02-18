#!/usr/bin/env python3
"""Launch script for the XRPL DEX Trading Bot."""

import sys

from bot.main import run_bot


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    run_bot(config_path)


if __name__ == "__main__":
    main()
