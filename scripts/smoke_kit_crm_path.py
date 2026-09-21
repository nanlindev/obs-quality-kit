#!/usr/bin/env python3
"""P2-3 — crm thin adapter B smoke (OBS subset: health / gate / Jaeger).

Modes:
  (default)  static Review checks; if CRM sidecar reachable → live OBS asserts
  --static-only   never call the network
  --live          require sidecar (+ Jaeger)

Env:
  CRM_WORKFLOW_PATH   default ../crm-workflow (relative to kit root)
  CRM_SIDECAR_URL     default http://127.0.0.1:8002
  OBS_JAEGER_UI       default http://127.0.0.1:16686
  OBS_SMOKE_JAEGER_WAIT_S  default 15

Exit 0 = pass. No sibling smoke_*_primary — OBS subset only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
LIB = ROOT / "scripts"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from lib.adapter_path_smoke import run_adapter_smoke  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--live", action="store_true", help="require live sidecar+Jaeger")
    args = parser.parse_args(argv)
    return run_adapter_smoke(
        kit_root=ROOT,
        name="crm",
        adapter_stem="CRM_ADAPTER",
        sibling_env="CRM_WORKFLOW_PATH",
        sibling_default="../crm-workflow",
        sidecar_env="CRM_SIDECAR_URL",
        sidecar_default="http://127.0.0.1:8002",
        prefix="C",
        require_database_ok=False,
        static_only=args.static_only,
        live_required=args.live,
    )


if __name__ == "__main__":
    sys.exit(main())
