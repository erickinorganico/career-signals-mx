"""Compatibility entry point for installed official reconciliation."""

from brujula.official_reconciliation import *  # noqa: F401,F403
from brujula.official_reconciliation import main

if __name__ == "__main__":
    raise SystemExit(main())
