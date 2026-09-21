#!/usr/bin/env python3
"""P2-7 — Phase-2 regression pack (P1 gate + P2 adapters / loki / llm ops).

Does NOT film demos. Exit 0 = P2 smoke gate green (status → 0.2-p2-smoke-green).
Film remains P2-8.

Usage (prefer stacks already up):
  python3 scripts/smoke_kit_p2.py
  python3 scripts/smoke_kit_p2.py --static-only
  python3 scripts/smoke_kit_p2.py --p1-static          # P1 static + P2 live
  python3 scripts/smoke_kit_p2.py --skip-p1            # P2 pieces only
  python3 scripts/smoke_kit_p2.py --skip-doc-primary

Env: same as individual smokes (DOC_SIDECAR_URL, ECOM_SIDECAR_URL, CRM_SIDECAR_URL, …).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(label: str, argv: list[str]) -> None:
    print(f"\n======== {label} ========")
    print("+", " ".join(argv))
    proc = subprocess.run(argv, cwd=str(ROOT))
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    print(f"OK  {label}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profiles",
        default="base,metrics,langfuse,full",
        help="forwarded to smoke_kit_p1 for layer A (ignored with --skip-p1 / --p1-static)",
    )
    parser.add_argument(
        "--skip-doc-primary",
        action="store_true",
        help="forward --skip-primary to smoke_kit_p1 / doc-path",
    )
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="P1 static + ecom/crm/llm static (no Docker live)",
    )
    parser.add_argument(
        "--p1-static",
        action="store_true",
        help="run smoke_kit_p1 --static-only then P2 live pieces",
    )
    parser.add_argument(
        "--skip-p1",
        action="store_true",
        help="skip smoke_kit_p1 entirely (P2 pieces only)",
    )
    parser.add_argument(
        "--skip-loki",
        action="store_true",
        help="skip smoke_kit_bootstrap --profile loki",
    )
    args = parser.parse_args(argv)
    py = sys.executable

    if args.static_only:
        _run(
            "p1-static",
            [py, str(ROOT / "scripts" / "smoke_kit_p1.py"), "--static-only"],
        )
        _run(
            "ecom-static",
            [py, str(ROOT / "scripts" / "smoke_kit_ecom_path.py"), "--static-only"],
        )
        _run(
            "crm-static",
            [py, str(ROOT / "scripts" / "smoke_kit_crm_path.py"), "--static-only"],
        )
        _run(
            "llm-ops-static",
            [py, str(ROOT / "scripts" / "smoke_kit_llm_ops.py"), "--static-only"],
        )
        print("\nOK  smoke_kit_p2 passed (static-only) — not a full P2 close")
        return 0

    if not args.skip_p1:
        p1 = [py, str(ROOT / "scripts" / "smoke_kit_p1.py")]
        if args.p1_static:
            p1.append("--static-only")
        else:
            p1.extend(["--profiles", args.profiles])
            if args.skip_doc_primary:
                p1.append("--skip-doc-primary")
        _run("p1-gate", p1)
    else:
        # Still need handbook pack when skipping full p1
        _run("docs", [py, str(ROOT / "scripts" / "smoke_kit_docs.py")])

    _run("ecom-path", [py, str(ROOT / "scripts" / "smoke_kit_ecom_path.py")])
    _run("crm-path", [py, str(ROOT / "scripts" / "smoke_kit_crm_path.py")])

    if not args.skip_loki:
        _run(
            "bootstrap:loki",
            [py, str(ROOT / "scripts" / "smoke_kit_bootstrap.py"), "--profile", "loki"],
        )

    llm = [py, str(ROOT / "scripts" / "smoke_kit_llm_ops.py")]
    _run("llm-ops", llm)

    print("\n======== P2 smoke gate ========")
    print("OK  smoke_kit_p2 passed — Phase-2 smoke-green (P2-0…P2-7)")
    print("NOTE  film = P2-8 only; do not cut Fiverr 75s yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
