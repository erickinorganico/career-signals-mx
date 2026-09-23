"""Compatibility entry point for installed numerical acceptance."""

from brujula.enoe_acceptance import *  # noqa: F401,F403
from brujula.enoe_acceptance import (
    _canonical_research_content, _code_hashes, _digest, _verify_result, main,
)

if __name__ == "__main__":
    raise SystemExit(main())
