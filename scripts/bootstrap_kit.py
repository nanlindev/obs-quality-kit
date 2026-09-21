#!/usr/bin/env python3
"""OBS Quality Kit bootstrap — base / metrics / langfuse / full / loki.

Usage:
  python3 scripts/bootstrap_kit.py preflight [--profile base|metrics|langfuse|full|loki]
  python3 scripts/bootstrap_kit.py up [--profile ...] [--brownfield adopt|rebind|abort]
  python3 scripts/bootstrap_kit.py down [--profile ...] [--force] [--volumes]
  python3 scripts/bootstrap_kit.py status [--profile ...]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from lib.langfuse_stack import (  # noqa: E402
    langfuse_ui_healthy,
    start_langfuse,
    stop_langfuse,
    wait_langfuse_healthy,
)
from lib.loki import (  # noqa: E402
    loki_endpoints_healthy,
    start_loki,
    stop_loki,
    wait_loki_healthy,
)
from lib.metrics import (  # noqa: E402
    metrics_endpoints_healthy,
    start_metrics,
    stop_metrics,
    wait_metrics_healthy,
)
from lib.paths import STATE_FILE, SUPPORTED_PROFILES, load_dotenv, profile_name  # noqa: E402
from lib.preflight import run_preflight  # noqa: E402
from lib.stacks import (  # noqa: E402
    BASE_STACKS,
    BootstrapState,
    bind_host,
    cleanup_hint,
    detect_conflicts,
    endpoints_healthy,
    ensure_networks,
    kit_projects_running,
    render_all,
    resolve_brownfield,
    start_stacks,
    stop_stacks,
    wait_healthy,
)


def _wants_metrics(profile: str) -> bool:
    return profile in ("metrics", "full")


def _wants_langfuse(profile: str) -> bool:
    return profile in ("langfuse", "full")


def _wants_loki(profile: str) -> bool:
    return profile == "loki"


def _save_state(
    *,
    profile: str,
    brownfield: str,
    started: list[str],
    adopted: list[str],
    rendered: dict[str, str],
    bind: str,
    metrics: bool,
    langfuse: bool,
    loki: bool,
) -> None:
    BootstrapState(
        profile=profile,
        brownfield=brownfield,
        started=started,
        adopted=adopted,
        rendered=rendered,
        bind_host=bind,
        metrics=metrics,
        langfuse=langfuse,
        loki=loki,
    ).save()


def _ensure_metrics() -> int:
    try:
        ok, notes = metrics_endpoints_healthy()
        if ok:
            for n in notes:
                print(f"OK  {n}")
            print("OK  metrics already healthy (idempotent)")
            return 0
        start_metrics()
        wait_metrics_healthy(timeout_s=180)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  metrics up error: {exc}", file=sys.stderr)
        print(cleanup_hint(), file=sys.stderr)
        return 1


def _ensure_langfuse() -> int:
    try:
        ok, note = langfuse_ui_healthy()
        if ok:
            print(f"OK  {note}")
            print("OK  langfuse already healthy (idempotent)")
            return 0
        start_langfuse()
        wait_langfuse_healthy(timeout_s=360)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  langfuse up error: {exc}", file=sys.stderr)
        print(cleanup_hint(), file=sys.stderr)
        return 1


def _ensure_loki() -> int:
    try:
        ok, notes = loki_endpoints_healthy()
        if ok:
            for n in notes:
                print(f"OK  {n}")
            print("OK  loki already healthy (idempotent)")
            return 0
        start_loki()
        wait_loki_healthy(timeout_s=180)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  loki up error: {exc}", file=sys.stderr)
        print(cleanup_hint(), file=sys.stderr)
        return 1


def _preserve_addon_flags(prev: BootstrapState | None) -> tuple[bool, bool, bool]:
    """Keep co-running addons in state when switching profiles (e.g. metrics then loki)."""
    metrics_ok = False
    langfuse_ok = False
    loki_ok = False
    if prev and prev.metrics:
        try:
            mok, _ = metrics_endpoints_healthy()
            metrics_ok = mok
        except Exception:  # noqa: BLE001 — slow host / probe timeout must not abort up
            metrics_ok = False
    if prev and prev.langfuse:
        try:
            lok, _ = langfuse_ui_healthy()
            langfuse_ok = lok
        except Exception:  # noqa: BLE001
            langfuse_ok = False
    if prev and prev.loki:
        try:
            loki_h, _ = loki_endpoints_healthy()
            loki_ok = loki_h
        except Exception:  # noqa: BLE001
            loki_ok = False
    return metrics_ok, langfuse_ok, loki_ok


def cmd_preflight(args: argparse.Namespace) -> int:
    load_dotenv()
    report = run_preflight(profile=profile_name(args.profile), check_ports_free=False)
    report.print()
    return 0 if report.ok else 1


def cmd_status(args: argparse.Namespace) -> int:
    load_dotenv()
    profile = profile_name(args.profile)
    state = BootstrapState.load()
    print(f"profile={profile}")
    if state:
        print(f"state={state.to_json()}")
    else:
        print("state=<none>")
    conflicts = detect_conflicts()
    print(f"conflicts={conflicts}")
    ok, notes = endpoints_healthy()
    for n in notes:
        print(("OK  " if ok else "…  ") + n)
    if _wants_metrics(profile) or (state and state.metrics):
        mok, mnotes = metrics_endpoints_healthy()
        for n in mnotes:
            print(("OK  " if mok else "…  ") + n)
        ok = ok and mok
    if _wants_langfuse(profile) or (state and state.langfuse):
        lok, lnote = langfuse_ui_healthy()
        print(("OK  " if lok else "…  ") + lnote)
        ok = ok and lok
    if _wants_loki(profile) or (state and state.loki):
        loki_h, lnotes = loki_endpoints_healthy()
        for n in lnotes:
            print(("OK  " if loki_h else "…  ") + n)
        ok = ok and loki_h
    return 0 if ok else 1


def cmd_up(args: argparse.Namespace) -> int:
    load_dotenv()
    profile = profile_name(args.profile)
    if profile not in SUPPORTED_PROFILES:
        print(
            f"FAIL  profile={profile} not implemented "
            f"(supported: {', '.join(SUPPORTED_PROFILES)})",
            file=sys.stderr,
        )
        return 2

    want_metrics = _wants_metrics(profile)
    want_langfuse = _wants_langfuse(profile)
    want_loki = _wants_loki(profile)
    mode = resolve_brownfield(args.brownfield)
    bind = bind_host()

    report = run_preflight(profile=profile, check_ports_free=False)
    report.print()
    if not report.ok:
        print("FAIL  preflight blocked bootstrap (no pull started)", file=sys.stderr)
        return 1

    conflicts = detect_conflicts()
    any_busy = any(conflicts["busy_ports"].values())
    any_containers = any(conflicts["containers"].values())
    conflict = any_busy or any_containers
    base_ok = False
    rendered: dict[str, str] = {}
    started: list[str] = []
    adopted: list[str] = []
    brownfield_rec = mode

    if conflict and mode == "abort":
        if kit_projects_running():
            ok, notes = endpoints_healthy()
            if ok:
                for n in notes:
                    print(f"OK  {n}")
                plans = render_all(bind)
                rendered = {p.name: str(p.rendered_compose) for p in plans}
                started = list(BASE_STACKS)
                brownfield_rec = "fresh"
                base_ok = True
                print("OK  idempotent re-run: kit O+J already healthy")
            else:
                print(
                    "FAIL  brownfield conflict and kit O+J unhealthy; "
                    "try down then up, or --brownfield adopt|rebind",
                    file=sys.stderr,
                )
                return 1
        else:
            print(
                "FAIL  brownfield conflict detected; refusing to double-start.\n"
                f"  details={conflicts}\n"
                "  choose: --brownfield adopt | rebind | abort",
                file=sys.stderr,
            )
            return 1

    elif conflict and mode == "adopt":
        ok, notes = endpoints_healthy()
        for n in notes:
            print(("OK  " if ok else "FAIL") + f"  {n}")
        if not ok:
            print(
                "FAIL  --brownfield adopt requires healthy OTLP + Jaeger UI endpoints",
                file=sys.stderr,
            )
            return 1
        if kit_projects_running():
            plans = render_all(bind)
            rendered = {p.name: str(p.rendered_compose) for p in plans}
            started = list(BASE_STACKS)
            brownfield_rec = "fresh"
            print("OK  kit O+J already running (recorded as started; idempotent)")
        else:
            adopted = list(BASE_STACKS)
            brownfield_rec = "adopt"
            print("OK  adopted existing O+J (idempotent; no new containers started)")
        base_ok = True

    elif conflict and mode == "rebind":
        still_busy = [k for k, v in conflicts["busy_ports"].items() if v]
        if still_busy:
            print(
                "FAIL  --brownfield rebind still sees busy ports "
                f"{still_busy}. Set free OBS_*_PORT in .env first.",
                file=sys.stderr,
            )
            return 1
        mode = "fresh"

    if not base_ok:
        if not conflict:
            mode = "fresh" if mode in ("abort", "rebind", "fresh") else mode

        ok_now, notes_now = endpoints_healthy()
        state_prev = BootstrapState.load()
        if ok_now and kit_projects_running():
            for n in notes_now:
                print(f"OK  {n}")
            plans = render_all(bind)
            rendered = {p.name: str(p.rendered_compose) for p in plans}
            started = list(BASE_STACKS)
            brownfield_rec = "fresh"
            base_ok = True
            print("OK  idempotent re-run: kit endpoints already healthy")
        elif ok_now and state_prev and state_prev.adopted:
            for n in notes_now:
                print(f"OK  {n}")
            adopted = list(BASE_STACKS)
            brownfield_rec = "adopt"
            base_ok = True
            print("OK  idempotent re-run: adopted endpoints already healthy")
        else:
            try:
                ensure_networks()
                plans = render_all(bind)
                start_stacks(plans)
                rendered = {p.name: str(p.rendered_compose) for p in plans}
                started = list(BASE_STACKS)
                brownfield_rec = "fresh"
                _save_state(
                    profile=profile,
                    brownfield=brownfield_rec,
                    started=started,
                    adopted=[],
                    rendered=rendered,
                    bind=bind,
                    metrics=False,
                    langfuse=False,
                    loki=False,
                )
                wait_healthy(timeout_s=240)
                base_ok = True
            except Exception as exc:  # noqa: BLE001
                print(f"FAIL  bootstrap up error: {exc}", file=sys.stderr)
                print(cleanup_hint(), file=sys.stderr)
                return 1

    if not base_ok:
        print("FAIL  base O+J not ready", file=sys.stderr)
        return 1

    prev = BootstrapState.load()
    metrics_ok, langfuse_ok, loki_ok = _preserve_addon_flags(prev)

    if want_metrics:
        rc = _ensure_metrics()
        if rc != 0:
            _save_state(
                profile=profile,
                brownfield=brownfield_rec,
                started=started,
                adopted=adopted,
                rendered=rendered,
                bind=bind,
                metrics=False,
                langfuse=langfuse_ok,
                loki=loki_ok,
            )
            return rc
        metrics_ok = True

    if want_langfuse:
        rc = _ensure_langfuse()
        if rc != 0:
            _save_state(
                profile=profile,
                brownfield=brownfield_rec,
                started=started,
                adopted=adopted,
                rendered=rendered,
                bind=bind,
                metrics=metrics_ok,
                langfuse=False,
                loki=loki_ok,
            )
            return rc
        langfuse_ok = True

    if want_loki:
        rc = _ensure_loki()
        if rc != 0:
            _save_state(
                profile=profile,
                brownfield=brownfield_rec,
                started=started,
                adopted=adopted,
                rendered=rendered,
                bind=bind,
                metrics=metrics_ok,
                langfuse=langfuse_ok,
                loki=False,
            )
            return rc
        loki_ok = True

    _save_state(
        profile=profile,
        brownfield=brownfield_rec,
        started=started,
        adopted=adopted,
        rendered=rendered,
        bind=bind,
        metrics=metrics_ok,
        langfuse=langfuse_ok,
        loki=loki_ok,
    )
    print(f"OK  bootstrap up complete (profile={profile})")
    return 0


def cmd_down(args: argparse.Namespace) -> int:
    load_dotenv()
    profile = profile_name(args.profile)
    state = BootstrapState.load()

    # Addon-scoped down: stop ONLY that addon — never siblings or O+J.
    if profile in ("metrics", "langfuse", "loki"):
        try:
            if profile == "metrics":
                stop_metrics(volumes=args.volumes)
                if state:
                    state.metrics = False
                    state.profile = state.profile if state.profile != "metrics" else "base"
                    state.save()
            elif profile == "langfuse":
                stop_langfuse(volumes=args.volumes)
                if state:
                    state.langfuse = False
                    state.profile = state.profile if state.profile != "langfuse" else "base"
                    state.save()
            else:
                stop_loki(volumes=args.volumes)
                if state:
                    state.loki = False
                    state.profile = state.profile if state.profile != "loki" else "base"
                    state.save()
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL  addon down error: {exc}", file=sys.stderr)
            return 1
        print(
            f"OK  addon down complete (profile={profile}; "
            "siblings and O+J left running)"
        )
        return 0

    # base / full: tear down kit-managed addons + O+J
    if profile == "full":
        stop_m = stop_lf = stop_lk = True
    else:
        # base (and any other non-addon profile): stop addons recorded in state
        stop_m = bool(state and state.metrics)
        stop_lf = bool(state and state.langfuse)
        stop_lk = bool(state and state.loki)

    if state and state.adopted and not args.force:
        try:
            if stop_lf:
                stop_langfuse(volumes=args.volumes)
            if stop_m:
                stop_metrics(volumes=args.volumes)
            if stop_lk:
                stop_loki(volumes=args.volumes)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL  addon down error: {exc}", file=sys.stderr)
            return 1
        print(
            "OK  state is adopt — refusing to stop foreign O+J stacks.\n"
            f"  Use --force to down obs-kit-* O+J too.\n  {cleanup_hint()}"
        )
        if state:
            state.metrics = False
            state.langfuse = False
            state.loki = False
            state.save()
        return 0

    try:
        if stop_lf:
            stop_langfuse(volumes=args.volumes)
        if stop_m:
            stop_metrics(volumes=args.volumes)
        if stop_lk:
            stop_loki(volumes=args.volumes)
        plans = render_all(bind_host())
        stop_stacks(plans, volumes=args.volumes)
    except FileNotFoundError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  down error: {exc}", file=sys.stderr)
        return 1

    if STATE_FILE.is_file():
        STATE_FILE.unlink()
    print("OK  bootstrap down complete")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OBS Quality Kit bootstrap")
    sub = p.add_subparsers(dest="command", required=True)

    def add_profile(sp: argparse.ArgumentParser) -> None:
        sp.add_argument(
            "--profile",
            default=None,
            help="base|metrics|langfuse|full|loki",
        )

    sp = sub.add_parser("preflight", help="Run preflight only (no pull)")
    add_profile(sp)
    sp.set_defaults(func=cmd_preflight)

    sp = sub.add_parser("up", help="Preflight + start profile stacks")
    add_profile(sp)
    sp.add_argument(
        "--brownfield",
        choices=["adopt", "rebind", "abort"],
        default=None,
        help="Conflict policy for O+J (default OBS_BROWNFIELD or abort)",
    )
    sp.set_defaults(func=cmd_up)

    sp = sub.add_parser("down", help="Stop kit-started stacks")
    add_profile(sp)
    sp.add_argument("--force", action="store_true")
    sp.add_argument("--volumes", action="store_true", help="Also remove named volumes")
    sp.set_defaults(func=cmd_down)

    sp = sub.add_parser("status", help="Show state + endpoint health")
    add_profile(sp)
    sp.set_defaults(func=cmd_status)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
