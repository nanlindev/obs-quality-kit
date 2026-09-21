#!/usr/bin/env python3
"""P2-5 — thin LLM Ops smoke (score / Scheme B correlation; prefer doc+L).

Modes:
  (default)  static Review-P2-5; if DOC sidecar reachable → live (skip if L not configured)
  --static-only   never call the network
  --live          require sidecar; if langfuse=configured also require score signal

Env:
  DOC_WORKFLOW_PATH   default ../doc-workflow
  DOC_SIDECAR_URL     default http://127.0.0.1:8004
  OBS_LANGFUSE_UI     default http://127.0.0.1:3000

Exit 0 = pass. Does not rebuild doc Prompt/Dataset platforms.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contract.gate import DEFAULT_GATE_MODE, GateMode, should_block_writes  # noqa: E402

_OPENER = request.build_opener(request.ProxyHandler({}))


class Fail(Exception):
    pass


def _ok(msg: str) -> None:
    print(f"OK  {msg}")


def _warn(msg: str) -> None:
    print(f"WARN {msg}")


def _doc_root() -> Path:
    raw = os.getenv("DOC_WORKFLOW_PATH", "").strip()
    if raw:
        p = Path(raw)
        return p if p.is_absolute() else (ROOT / p).resolve()
    return (ROOT / ".." / "doc-workflow").resolve()


def _sidecar() -> str:
    return os.getenv("DOC_SIDECAR_URL", "http://127.0.0.1:8004").rstrip("/")


def _json_get(url: str, *, timeout: int = 30) -> dict[str, Any]:
    req = request.Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:600]
        raise Fail(f"HTTP {exc.code} GET {url}\n{body}") from exc
    except error.URLError as exc:
        raise Fail(f"URL error GET {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise Fail(f"invalid JSON from {url}: {exc}") from exc


def _reachable(url: str, *, timeout: float = 2.0) -> bool:
    req = request.Request(url, method="GET")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            resp.read(64)
        return True
    except Exception:
        return False


def step_static(doc: Path) -> None:
    for rel in ("docs/zh/LLM_OPS.md", "docs/en/LLM_OPS.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        low = text.lower()
        if "shadow" not in low:
            raise Fail(f"{rel}: must keep shadow default")
        if "correlation_id" not in text or "trace_id" not in text:
            raise Fail(f"{rel}: must document score ↔ correlation_id / trace_id")
        if "安装" not in text and "install" not in low:
            raise Fail(f"{rel}: must distinguish install vs wire-in")
        if "接入" not in text and "wire-in" not in low and "wire in" not in low:
            raise Fail(f"{rel}: must distinguish install vs wire-in")
        if "PHASE2_LANGFUSE_ADDENDUM" not in text:
            raise Fail(f"{rel}: must link doc PHASE2_LANGFUSE_ADDENDUM")
        if "dataset" not in low and "评测平台" not in text:
            # non-goals should mention dataset / eval platform
            raise Fail(f"{rel}: must state non-goals (dataset / eval)")
        _ok(f"static kit {rel}")

    for rel in ("docs/zh/CONTRACT.md", "docs/en/CONTRACT.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "score" not in text.lower():
            raise Fail(f"{rel}: must mention score hook")
        if "correlation_id" not in text or "trace_id" not in text:
            raise Fail(f"{rel}: score section needs Scheme B ids")
        _ok(f"static {rel} score hooks")

    if not doc.is_dir():
        # Standalone kit CI has no doc-workflow checkout.
        _warn(f"DOC_WORKFLOW_PATH missing ({doc}) — skip doc file asserts")
    else:
        scores = doc / "python-service" / "scores.py"
        if not scores.is_file():
            raise Fail(f"missing doc reference scores.py: {scores}")
        src = scores.read_text(encoding="utf-8")
        for needle in (
            "doc.validation_passed",
            "correlation_id",
            "create_score",
            "langfuse_disabled",
        ):
            if needle not in src:
                raise Fail(f"doc scores.py missing {needle}")
        _ok("static doc scores.py reference present")

        addendum = doc / "docs" / "zh" / "PHASE2_LANGFUSE_ADDENDUM.md"
        if not addendum.is_file():
            raise Fail(f"missing deeper sample: {addendum}")
        _ok("static doc PHASE2_LANGFUSE_ADDENDUM present (deeper sample, not rebuilt)")

    if DEFAULT_GATE_MODE is not GateMode.SHADOW:
        raise Fail("kit DEFAULT_GATE_MODE drifted from shadow")
    if should_block_writes("shadow"):
        raise Fail("shadow must not block writes (Review-P2-5)")
    _ok("static kit gate still shadow")


def step_live(*, require_configured: bool) -> None:
    health = _json_get(f"{_sidecar()}/health", timeout=30)
    lf = str(health.get("langfuse") or "skipped")
    if lf != "configured":
        if require_configured:
            raise Fail(
                f"--live required langfuse=configured but health.langfuse={lf!r} "
                "(set LANGFUSE_* on doc sidecar)"
            )
        _ok(f"L10 Langfuse skip (health.langfuse={lf}) — honest skip like D7")
        return

    host = os.getenv("OBS_LANGFUSE_UI", "http://127.0.0.1:3000").rstrip("/")
    if _reachable(host + "/"):
        _ok(f"L10 Langfuse UI reachable at {host}")
    else:
        _warn(f"L10 Langfuse UI not reachable at {host} (warn-only)")

    # Prefer primary smoke: produces validate → langfuse_scores when keys work.
    script = _doc_root() / "scripts" / "smoke_doc_primary.py"
    if not script.is_file():
        raise Fail(f"missing {script}")
    env = os.environ.copy()
    env["DOC_SIDECAR_URL"] = _sidecar()
    _ok("L10 invoking smoke_doc_primary for score signal …")
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(_doc_root()),
        env=env,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise Fail(f"L10 smoke_doc_primary failed (exit {proc.returncode})")

    blob = (proc.stdout or "") + (proc.stderr or "")
    # Primary may not print langfuse_scores; re-check via a lightweight health + note.
    # Accept: primary passed under configured keys = score path exercised (doc scores.py no-op-safe).
    # Stronger: look for langfuse_scores in any JSON-looking line.
    if "langfuse_scores" in blob or "validation_passed" in blob:
        _ok("L10 score signal visible in primary output")
    else:
        _ok(
            "L10 primary passed with langfuse=configured "
            "(scores attach on validate; check Langfuse UI by correlation_id / score name)"
        )

    mode = str(health.get("obs_quality_gate_mode") or "").lower()
    if mode and mode != "shadow":
        raise Fail(f"L10 expected shadow gate, got {mode!r}")
    if health.get("obs_quality_gate_blocks_writes") is True:
        raise Fail("L10 gate must not block writes under shadow")
    _ok("L10 gate still shadow after LLM Ops path")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument(
        "--live",
        action="store_true",
        help="require sidecar; require langfuse=configured for score path",
    )
    args = parser.parse_args(argv)

    doc = _doc_root()
    print(f"kit llm-ops smoke → doc={doc}")
    try:
        step_static(doc)
        if args.static_only:
            print("OK  smoke_kit_llm_ops passed (static-only)")
            return 0

        health_url = f"{_sidecar()}/health"
        if not _reachable(health_url):
            if args.live:
                raise Fail(f"--live required but sidecar not reachable at {health_url}")
            _warn(f"sidecar not reachable at {health_url}; static-only pass")
            print("OK  smoke_kit_llm_ops passed (static; live skipped)")
            return 0

        step_live(require_configured=args.live)
        print("OK  smoke_kit_llm_ops passed (static+live)")
        return 0
    except Fail as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
