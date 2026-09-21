"""Shared OBS subset asserts for vertical thin adapters (ecom / crm / similar).

Used by smoke_kit_ecom_path.py and smoke_kit_crm_path.py.
Does not run sibling business primary smokes (none for ecom/crm yet).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib import error, request

from contract.gate import DEFAULT_GATE_MODE, GateMode, should_block_writes
from contract.ids import is_valid_correlation_id, is_valid_trace_id

_OPENER = request.build_opener(request.ProxyHandler({}))


class Fail(Exception):
    pass


def ok(msg: str) -> None:
    print(f"OK  {msg}")


def warn(msg: str) -> None:
    print(f"WARN {msg}")


def json_get(url: str, *, timeout: int = 30) -> dict[str, Any]:
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


def reachable(url: str, *, timeout: float = 2.0) -> bool:
    req = request.Request(url, method="GET")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            resp.read(64)
        return True
    except Exception:
        return False


def jaeger_ui() -> str:
    return os.getenv("OBS_JAEGER_UI", "http://127.0.0.1:16686").rstrip("/")


def resolve_sibling(env_key: str, default_rel: str, *, kit_root: Path) -> Path:
    raw = os.getenv(env_key, "").strip()
    if raw:
        p = Path(raw)
        return p if p.is_absolute() else (kit_root / p).resolve()
    return (kit_root / default_rel).resolve()


def step_static_adapter(
    *,
    kit_root: Path,
    sibling: Path,
    adapter_stem: str,
    smoke_name: str,
    require_db_in_health: bool = False,
) -> None:
    del require_db_in_health  # documented for callers; live check uses flag
    for rel in (f"docs/zh/{adapter_stem}.md", f"docs/en/{adapter_stem}.md"):
        text = (kit_root / rel).read_text(encoding="utf-8")
        low = text.lower()
        if "不搬" not in text and "do not relocate" not in low and "不搬仓" not in text:
            if "stays independent" not in low and "仓仍独立" not in text:
                raise Fail(f"{rel}: must state repo stays independent / no relocate")
        if "shadow" not in low:
            raise Fail(f"{rel}: must document shadow default")
        ok(f"static kit {rel}")

    if not sibling.is_dir():
        # Standalone kit CI (GitHub Actions) has no sibling checkout — kit docs
        # above still ran; sibling file asserts are local/lindev-only.
        warn(f"sibling missing ({sibling}) — skip vertical file asserts ({smoke_name})")
    else:
        env_ex = (sibling / ".env.example").read_text(encoding="utf-8")
        if "OBS_QUALITY_GATE_MODE=shadow" not in env_ex:
            raise Fail(f"{sibling.name} .env.example missing OBS_QUALITY_GATE_MODE=shadow")
        ok(f"static {sibling.name} .env.example gate=shadow")

        compose = (sibling / "docker" / "compose.yml").read_text(encoding="utf-8")
        if "OBS_QUALITY_GATE_MODE" not in compose:
            raise Fail(f"{sibling.name} docker/compose.yml missing OBS_QUALITY_GATE_MODE")
        ok(f"static {sibling.name} compose injects OBS_QUALITY_GATE_MODE")

        qg = sibling / "python-service" / "quality_gate.py"
        if not qg.is_file():
            raise Fail(f"missing thin adapter module: {qg}")
        qg_src = qg.read_text(encoding="utf-8")
        if "DEFAULT_GATE_MODE" not in qg_src or "shadow" not in qg_src.lower():
            raise Fail("quality_gate.py must default to shadow")
        if "should_block_writes" not in qg_src:
            raise Fail("quality_gate.py must expose should_block_writes")
        ok(f"static {sibling.name} quality_gate.py present")

        main_src = (sibling / "python-service" / "main.py").read_text(encoding="utf-8")
        for needle in (
            "obs_quality_gate_mode",
            "obs_quality_gate_blocks_writes",
            "current_gate_mode",
        ):
            if needle not in main_src:
                raise Fail(f"{sibling.name} /health adapter missing {needle} in main.py")
        ok(f"static {sibling.name} /health exposes gate fields")

        obs_zh = sibling / "docs" / "zh" / "OBSERVABILITY.md"
        if obs_zh.is_file():
            obs_text = obs_zh.read_text(encoding="utf-8")
            if adapter_stem not in obs_text and "obs-quality-kit" not in obs_text.lower():
                raise Fail(f"{sibling.name} docs/zh/OBSERVABILITY.md should link kit adapter")
            ok(f"static {sibling.name} OBSERVABILITY links kit")

    if DEFAULT_GATE_MODE is not GateMode.SHADOW:
        raise Fail("kit contract DEFAULT_GATE_MODE drifted from shadow")
    if should_block_writes(None) or should_block_writes("shadow"):
        raise Fail("kit should_block_writes must be false for shadow/default")
    ok(f"static kit gate still shadow ({smoke_name})")


def step_health(
    sidecar_url: str,
    *,
    prefix: str,
    require_database_ok: bool,
) -> dict[str, Any]:
    body = json_get(f"{sidecar_url.rstrip('/')}/health", timeout=30)
    if body.get("status") not in {"healthy", "degraded"}:
        raise Fail(f"{prefix}1 unexpected health status: {body}")
    if require_database_ok and body.get("database") != "ok":
        raise Fail(f"{prefix}1 database not ok: {body}")
    corr = body.get("correlation_id")
    tid = body.get("trace_id")
    if not is_valid_correlation_id(str(corr or "")):
        raise Fail(f"{prefix}5 missing/invalid correlation_id: {corr!r}")
    if not is_valid_trace_id(str(tid or "")):
        raise Fail(f"{prefix}5 missing/invalid trace_id: {tid!r}")
    mode = str(body.get("obs_quality_gate_mode") or "").lower()
    if mode != "shadow":
        raise Fail(
            f"{prefix}9 expected obs_quality_gate_mode=shadow got {mode!r} "
            "(rebuild sidecar after adapter patch if field missing)"
        )
    if body.get("obs_quality_gate_blocks_writes") is True:
        raise Fail(f"{prefix}9 obs_quality_gate_blocks_writes must be false under shadow")
    ok(
        f"{prefix}1/{prefix}5/{prefix}9 health ok gate={mode} "
        f"corr={str(corr)[:8]}… trace={(str(tid))[:16]}…"
    )
    return body


def _jaeger_has_trace(trace_id: str, *, wait_s: float) -> bool:
    deadline = time.time() + wait_s
    url = f"{jaeger_ui()}/api/traces/{trace_id}"
    last_err = ""
    while time.time() < deadline:
        try:
            data = json_get(url, timeout=10)
            if data.get("data"):
                return True
            errs = data.get("errors") or []
            last_err = str(errs)
        except Fail as exc:
            last_err = str(exc)
        time.sleep(0.5)
    if last_err:
        warn(f"Jaeger last response: {last_err[:200]}")
    return False


def step_jaeger(trace_id: str, *, prefix: str) -> None:
    wait_s = float(os.getenv("OBS_SMOKE_JAEGER_WAIT_S", "15"))
    if not reachable(f"{jaeger_ui()}/"):
        raise Fail(f"{prefix}6 Jaeger UI not reachable at {jaeger_ui()} (start kit base profile)")
    if not _jaeger_has_trace(trace_id, wait_s=wait_s):
        raise Fail(
            f"{prefix}6 Jaeger has no span for trace_id={trace_id} after {wait_s}s "
            "(search Jaeger by trace_id, not correlation_id)"
        )
    ok(f"{prefix}6 Jaeger found trace_id={trace_id[:16]}…")


def step_negative(*, prefix: str) -> None:
    fake = "0" * 32
    url = f"{jaeger_ui()}/api/traces/{fake}"
    try:
        data = json_get(url, timeout=10)
    except Fail as exc:
        msg = str(exc)
        if "404" in msg or "not found" in msg.lower():
            ok(f"{prefix}8 fake trace_id → Jaeger miss (HTTP readable)")
            return
        raise
    if data.get("data"):
        raise Fail(f"{prefix}8 unexpected: fake all-zero trace_id returned spans")
    ok(f"{prefix}8 fake trace_id → empty Jaeger data (readable miss)")


def step_langfuse(health: dict[str, Any], *, prefix: str) -> None:
    lf = str(health.get("langfuse") or "skipped")
    if lf != "configured":
        ok(f"{prefix}7 Langfuse skip (health.langfuse={lf})")
        return
    host = os.getenv("OBS_LANGFUSE_UI", "http://127.0.0.1:3000").rstrip("/")
    if reachable(host + "/"):
        ok(f"{prefix}7 Langfuse UI reachable at {host} (keys configured on sidecar)")
    else:
        warn(f"{prefix}7 Langfuse configured on sidecar but UI not reachable at {host}")
        ok(f"{prefix}7 Langfuse soft-pass (configured; UI check warn-only)")


def run_live(
    sidecar_url: str,
    *,
    prefix: str,
    require_database_ok: bool,
) -> None:
    health = step_health(
        sidecar_url, prefix=prefix, require_database_ok=require_database_ok
    )
    step_jaeger(str(health["trace_id"]), prefix=prefix)
    step_negative(prefix=prefix)
    step_langfuse(health, prefix=prefix)


def run_adapter_smoke(
    *,
    kit_root: Path,
    name: str,
    adapter_stem: str,
    sibling_env: str,
    sibling_default: str,
    sidecar_env: str,
    sidecar_default: str,
    prefix: str,
    require_database_ok: bool,
    static_only: bool,
    live_required: bool,
) -> int:
    sibling = resolve_sibling(sibling_env, sibling_default, kit_root=kit_root)
    sidecar = os.getenv(sidecar_env, sidecar_default).rstrip("/")
    print(f"kit {name}-path smoke → sibling={sibling}")
    try:
        step_static_adapter(
            kit_root=kit_root,
            sibling=sibling,
            adapter_stem=adapter_stem,
            smoke_name=name,
        )
        if static_only:
            print(f"OK  smoke_kit_{name}_path passed (static-only)")
            return 0

        health_url = f"{sidecar}/health"
        up = reachable(health_url)
        if not up:
            if live_required:
                raise Fail(f"--live required but sidecar not reachable at {health_url}")
            warn(f"sidecar not reachable at {health_url}; static-only pass")
            print(f"OK  smoke_kit_{name}_path passed (static; live skipped)")
            return 0

        run_live(sidecar, prefix=prefix, require_database_ok=require_database_ok)
        print(f"OK  smoke_kit_{name}_path passed (static+live)")
        return 0
    except Fail as exc:
        print(f"FAIL {exc}", file=__import__("sys").stderr)
        return 1
