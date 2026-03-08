#!/usr/bin/env python3
"""Convenience script for replay command."""

import sys

from polymarket_arb.cli import app

if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else ""
    app(["replay", slug])
