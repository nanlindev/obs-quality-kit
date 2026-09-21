#!/usr/bin/env python3
"""Print a Scheme B ID example (correlation_id + trace_id + traceparent).

No n8n / Docker required.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contract import resolve_ids  # noqa: E402


def main() -> int:
    ids = resolve_ids(
        body_correlation_id=None,
        headers={},
    )
    print(json.dumps(ids.as_dict(), indent=2))
    print("--- response headers ---")
    print(json.dumps(ids.response_headers(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
