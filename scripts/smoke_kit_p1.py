#!/usr/bin/env python3
"""Stage 9 / P1 close — run full acceptance A + B (+ static packs).

Does NOT film demos. Exit 0 = P1 smoke gate green.

Usage (stacks already up preferred):
  python3 scripts/smoke_kit_p1.py
  python3 scripts/smoke_kit_p1.py --skip-doc-primary   # OBS B only, no LLM path
  python3 scripts/smoke_kit_p1.py --profiles base,metrics   # subset of A

Env: same as individual smokes (DOC_SIDECAR_URL, OBS_JAEGER_UI, …).
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
        help="comma-separated bootstrap profiles for layer A",
    )
    parser.add_argument(
        "--skip-doc-primary",
        action="store_true",
        help="pass --skip-primary to smoke_kit_doc_path",
    )
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="contract + facade + docs only (no Docker / sidecar)",
    )
    args = parser.parse_args(argv)
    py = sys.executable

    _run("contract", [py, str(ROOT / "scripts" / "smoke_kit_contract.py")])
    _run("facade", [py, str(ROOT / "scripts" / "smoke_kit_facade.py")])
    _run("docs", [py, str(ROOT / "scripts" / "smoke_kit_docs.py")])

    if args.static_only:
        print("\nOK  smoke_kit_p1 passed (static-only) — not a full P1 close")
        return 0

    for prof in [p.strip() for p in args.profiles.split(",") if p.strip()]:
        _run(
            f"bootstrap:{prof}",
            [py, str(ROOT / "scripts" / "smoke_kit_bootstrap.py"), "--profile", prof],
        )

    doc_cmd = [py, str(ROOT / "scripts" / "smoke_kit_doc_path.py"), "--live"]
    if args.skip_doc_primary:
        doc_cmd.append("--skip-primary")
    _run("doc-path-B", doc_cmd)

    print("\n======== P1 smoke gate ========")
    print("OK  smoke_kit_p1 passed (A+B) — Phase-1 acceptance green")
    print("NOTE  do not film; film gate = Phase-2 complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
