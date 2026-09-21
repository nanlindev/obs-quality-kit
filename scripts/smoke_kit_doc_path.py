#!/usr/bin/env python3
"""Stage 6 — doc thin adapter + golden-path B smoke (PRD §16.3 D1–D9).

Modes:
  (default)  static Review-6 checks; if DOC sidecar reachable → live OBS asserts
             and optionally run sibling smoke_doc_primary (D2–D4)
  --static-only   never call the network
  --live          require sidecar (+ Jaeger for D6/D8)
  --skip-primary  live OBS only (health / gate / Jaeger); skip smoke_doc_primary

Env:
  DOC_WORKFLOW_PATH   default ../doc-workflow (relative to kit root)
  DOC_SIDECAR_URL     default http://127.0.0.1:8004
  OBS_JAEGER_UI       default http://127.0.0.1:16686  (API under /api)
  OBS_SMOKE_JAEGER_WAIT_S  default 15

Exit 0 = pass.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contract.gate import DEFAULT_GATE_MODE, GateMode, should_block_writes  # noqa: E402
from contract.ids import is_valid_correlation_id, is_valid_trace_id  # noqa: E402

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


def _jaeger() -> str:
    return os.getenv("OBS_JAEGER_UI", "http://127.0.0.1:16686").rstrip("/")


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


# ----- static (Review-6) -----------------------------------------------------


def step_static(doc: Path) -> None:
    for rel in ("docs/zh/DOC_ADAPTER.md", "docs/en/DOC_ADAPTER.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        low = text.lower()
        if "不搬" not in text and "do not relocate" not in low and "不搬仓" not in text:
            if "stays independent" not in low and "仓仍独立" not in text:
                raise Fail(f"{rel}: must state repo stays independent / no relocate")
        if "shadow" not in low:
            raise Fail(f"{rel}: must document shadow default")
        _ok(f"static doc {rel}")

    if not doc.is_dir():
        raise Fail(f"DOC_WORKFLOW_PATH missing: {doc}")

    env_ex = (doc / ".env.example").read_text(encoding="utf-8")
    if "OBS_QUALITY_GATE_MODE=shadow" not in env_ex:
        raise Fail("doc .env.example missing OBS_QUALITY_GATE_MODE=shadow")
    _ok("static doc .env.example gate=shadow")

    compose = (doc / "docker" / "compose.yml").read_text(encoding="utf-8")
    if "OBS_QUALITY_GATE_MODE" not in compose:
        raise Fail("doc docker/compose.yml missing OBS_QUALITY_GATE_MODE")
    _ok("static doc compose injects OBS_QUALITY_GATE_MODE")

    qg = doc / "python-service" / "quality_gate.py"
    if not qg.is_file():
        raise Fail(f"missing thin adapter module: {qg}")
    qg_src = qg.read_text(encoding="utf-8")
    if "DEFAULT_GATE_MODE" not in qg_src or "shadow" not in qg_src.lower():
        raise Fail("quality_gate.py must default to shadow")
    if "should_block_writes" not in qg_src:
        raise Fail("quality_gate.py must expose should_block_writes")
    _ok("static doc quality_gate.py present")

    main_src = (doc / "python-service" / "main.py").read_text(encoding="utf-8")
    for needle in (
        "obs_quality_gate_mode",
        "obs_quality_gate_blocks_writes",
        "current_gate_mode",
    ):
        if needle not in main_src:
            raise Fail(f"doc /health adapter missing {needle} in main.py")
    _ok("static doc /health exposes gate fields")

    if DEFAULT_GATE_MODE is not GateMode.SHADOW:
        raise Fail("kit contract DEFAULT_GATE_MODE drifted from shadow")
    if should_block_writes(None) or should_block_writes("shadow"):
        raise Fail("kit should_block_writes must be false for shadow/default")
    _ok("static kit gate still shadow (D9 library)")


# ----- live ------------------------------------------------------------------


def step_d1_d5_d9_health() -> dict[str, Any]:
    body = _json_get(f"{_sidecar()}/health", timeout=30)
    if body.get("status") not in {"healthy", "degraded"}:
        raise Fail(f"D1 unexpected health status: {body}")
    if body.get("database") != "ok":
        raise Fail(f"D1 database not ok: {body}")
    corr = body.get("correlation_id")
    tid = body.get("trace_id")
    if not is_valid_correlation_id(str(corr or "")):
        raise Fail(f"D5 missing/invalid correlation_id: {corr!r}")
    if not is_valid_trace_id(str(tid or "")):
        raise Fail(f"D5 missing/invalid trace_id: {tid!r}")
    mode = str(body.get("obs_quality_gate_mode") or "").lower()
    if mode != "shadow":
        raise Fail(
            f"D9 expected obs_quality_gate_mode=shadow got {mode!r} "
            "(rebuild sidecar after Stage-6 patch if field missing)"
        )
    if body.get("obs_quality_gate_blocks_writes") is True:
        raise Fail("D9 obs_quality_gate_blocks_writes must be false under shadow")
    _ok(
        f"D1/D5/D9 health ok gate={mode} "
        f"corr={str(corr)[:8]}… trace={(str(tid))[:16]}…"
    )
    return body


def _jaeger_has_trace(trace_id: str, *, wait_s: float) -> bool:
    deadline = time.time() + wait_s
    url = f"{_jaeger()}/api/traces/{trace_id}"
    last_err = ""
    while time.time() < deadline:
        try:
            data = _json_get(url, timeout=10)
            if data.get("data"):
                return True
            errs = data.get("errors") or []
            last_err = str(errs)
        except Fail as exc:
            last_err = str(exc)
        time.sleep(0.5)
    if last_err:
        _warn(f"Jaeger last response: {last_err[:200]}")
    return False


def step_d6_jaeger(trace_id: str) -> None:
    wait_s = float(os.getenv("OBS_SMOKE_JAEGER_WAIT_S", "15"))
    if not _reachable(f"{_jaeger()}/"):
        raise Fail(f"D6 Jaeger UI not reachable at {_jaeger()} (start kit base profile)")
    if not _jaeger_has_trace(trace_id, wait_s=wait_s):
        raise Fail(
            f"D6 Jaeger has no span for trace_id={trace_id} after {wait_s}s "
            "(search Jaeger by trace_id, not correlation_id)"
        )
    _ok(f"D6 Jaeger found trace_id={trace_id[:16]}…")


def step_d8_negative() -> None:
    fake = "0" * 32
    url = f"{_jaeger()}/api/traces/{fake}"
    try:
        data = _json_get(url, timeout=10)
    except Fail as exc:
        # Some Jaeger builds 404 the whole request — still a readable miss.
        msg = str(exc)
        if "404" in msg or "not found" in msg.lower():
            _ok("D8 fake trace_id → Jaeger miss (HTTP readable)")
            return
        raise
    if data.get("data"):
        raise Fail("D8 unexpected: fake all-zero trace_id returned spans")
    _ok("D8 fake trace_id → empty Jaeger data (readable miss)")


def step_d7_langfuse(health: dict[str, Any]) -> None:
    lf = str(health.get("langfuse") or "skipped")
    if lf != "configured":
        _ok(f"D7 Langfuse skip (health.langfuse={lf})")
        return
    host = os.getenv("OBS_LANGFUSE_UI", "http://127.0.0.1:3000").rstrip("/")
    if _reachable(host + "/"):
        _ok(f"D7 Langfuse UI reachable at {host} (keys configured on sidecar)")
    else:
        _warn(f"D7 Langfuse configured on sidecar but UI not reachable at {host}")
        _ok("D7 Langfuse soft-pass (configured; UI check warn-only)")


def step_d2_d4_primary(doc: Path) -> None:
    script = doc / "scripts" / "smoke_doc_primary.py"
    if not script.is_file():
        raise Fail(f"missing {script}")
    env = os.environ.copy()
    env["DOC_SIDECAR_URL"] = _sidecar()
    _ok(f"D2–D4 invoking {script.name} …")
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(doc),
        env=env,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise Fail(f"D2–D4 smoke_doc_primary failed (exit {proc.returncode})")
    _ok("D2–D4 smoke_doc_primary passed (demo/bad/mismatch/dup + trail)")


def step_d5_trail_sample() -> None:
    """Lightweight ID-through check without full LLM path (complements primary)."""
    corr = str(uuid.uuid4())
    payload = json.dumps(
        {"stage": "received", "status": "ok", "message": "obs-kit-doc-smoke"}
    ).encode()
    req = request.Request(
        f"{_sidecar()}/events",
        data=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Correlation-Id": corr,
        },
        method="POST",
    )
    try:
        with _OPENER.open(req, timeout=30) as resp:
            body = json.loads(resp.read().decode() or "{}")
    except error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")[:400]
        raise Fail(f"D5 POST /events HTTP {exc.code}: {raw}") from exc
    except error.URLError as exc:
        raise Fail(f"D5 POST /events: {exc}") from exc

    got_corr = body.get("correlation_id") or corr
    trail = _json_get(f"{_sidecar()}/ops/trail?correlation_id={got_corr}", timeout=30)
    events = trail.get("events") or trail.get("items") or trail.get("trail") or []
    if not isinstance(events, list) or not events:
        raise Fail(f"D5 trail empty for correlation_id={got_corr}")
    blob = json.dumps(trail)
    if got_corr not in blob and corr not in blob:
        raise Fail("D5 trail JSON missing correlation_id")
    _ok(f"D5 trail events={len(events)} corr={str(got_corr)[:8]}…")


def run_live(*, skip_primary: bool) -> None:
    health = step_d1_d5_d9_health()
    step_d6_jaeger(str(health["trace_id"]))
    step_d8_negative()
    step_d7_langfuse(health)
    step_d5_trail_sample()
    if skip_primary:
        _warn("skipped D2–D4 (--skip-primary); run doc scripts/smoke_doc_primary.py manually")
        return
    step_d2_d4_primary(_doc_root())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--live", action="store_true", help="require live sidecar+Jaeger")
    parser.add_argument(
        "--skip-primary",
        action="store_true",
        help="live OBS asserts only; do not run smoke_doc_primary",
    )
    args = parser.parse_args(argv)

    doc = _doc_root()
    print(f"kit doc-path smoke → doc={doc}")
    try:
        step_static(doc)
        if args.static_only:
            print("OK  smoke_kit_doc_path passed (static-only)")
            return 0

        health_url = f"{_sidecar()}/health"
        up = _reachable(health_url)
        if not up:
            if args.live:
                raise Fail(f"--live required but sidecar not reachable at {health_url}")
            _warn(f"sidecar not reachable at {health_url}; static-only pass")
            print("OK  smoke_kit_doc_path passed (static; live skipped)")
            return 0

        run_live(skip_primary=args.skip_primary)
        print("OK  smoke_kit_doc_path passed (static+live)")
        return 0
    except Fail as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
