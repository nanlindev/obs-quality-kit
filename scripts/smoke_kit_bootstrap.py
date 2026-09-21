#!/usr/bin/env python3
"""Smoke acceptance A for obs-quality-kit (base / metrics / langfuse / full / loki).

PRD §16.2 automatable rows including B14–B16, B18 subset for Langfuse, B21 for Loki.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from lib import docker_util as duk  # noqa: E402
from lib.langfuse_stack import (  # noqa: E402
    assert_langfuse_down_fails_smoke,
    check_collector_langfuse_link,
    langfuse_image_audit,
    langfuse_ui_healthy,
    langfuse_ui_port,
)
from lib.loki import (  # noqa: E402
    assert_loki_negative,
    assert_loki_probe,
    check_loki_ui_binds,
    loki_endpoints_healthy,
    maybe_assert_grafana_loki_datasource,
)
from lib.metrics import (  # noqa: E402
    assert_grafana_dashboard,
    assert_prom_targets_up,
    check_metrics_ui_binds,
    metrics_endpoints_healthy,
)
from lib.paths import (  # noqa: E402
    BASE_PORTS,
    LOKI_PORTS,
    METRICS_PORTS,
    ROOT as KIT_ROOT,
    SUPPORTED_PROFILES,
    env,
    load_dotenv,
    profile_name,
)
from lib.preflight import run_preflight  # noqa: E402
from lib.stacks import BootstrapState, endpoints_healthy  # noqa: E402


class SmokeFailure(Exception):
    pass


def _ok(code: str, msg: str) -> None:
    print(f"OK  [{code}] {msg}")


def _fail(code: str, msg: str) -> None:
    raise SmokeFailure(f"[{code}] {msg}")


def _base_port(name: str) -> int:
    key, default = BASE_PORTS[name]
    return int(env(key, str(default)) or default)


def _metrics_port(name: str) -> int:
    key, default = METRICS_PORTS[name]
    return int(env(key, str(default)) or default)


def _jaeger_probe(bind: str, port: int) -> str:
    opener = request.build_opener(request.ProxyHandler({}))
    urls = [
        f"http://{bind}:{port}/api/services",
        f"http://127.0.0.1:{port}/api/services",
        f"http://{bind}:{port}/",
        f"http://127.0.0.1:{port}/",
    ]
    last_err = ""
    for url in urls:
        try:
            req = request.Request(url, headers={"Accept": "application/json,*/*"})
            with opener.open(req, timeout=5) as resp:
                body = resp.read().decode(errors="replace")[:500]
                return f"{url} → HTTP {resp.getcode()} ({body[:80]!r})"
        except error.HTTPError as exc:
            if exc.code < 500:
                return f"{url} → HTTP {exc.code}"
            last_err = f"{url} → HTTP {exc.code}"
        except error.URLError as exc:
            last_err = f"{url} → {exc}"
    raise SmokeFailure(f"Jaeger probe failed: {last_err}")


def _loki_port() -> int:
    key, default = LOKI_PORTS["loki"]
    return int(env(key, str(default)) or default)


def _check_ui_binds(
    *, include_metrics: bool, include_langfuse: bool, include_loki: bool
) -> None:
    allow = env("OBS_ALLOW_PUBLIC_UI", "") in ("1", "true", "yes")
    ui_port = _base_port("jaeger_ui")
    binds = duk.list_listening_binds(ui_port)
    public = [b for b in binds if b in ("0.0.0.0", "::", "[::]")]

    if include_metrics:
        public_m = check_metrics_ui_binds()
        if public_m and not allow:
            _fail("B19", f"metrics UI published publicly: {public_m}")
        if public_m and allow:
            _ok("B19", f"public metrics binds allowed (lab): {public_m}")
        else:
            _ok(
                "B19",
                "metrics UIs on loopback "
                f"(prom={_metrics_port('prometheus')} grafana={_metrics_port('grafana')})",
            )

    if include_langfuse:
        lf_port = langfuse_ui_port()
        lf_binds = duk.list_listening_binds(lf_port)
        public_l = [b for b in lf_binds if b in ("0.0.0.0", "::", "[::]")]
        if public_l and not allow:
            _fail("B19", f"Langfuse UI :{lf_port} published on {public_l}")
        if public_l and allow:
            _ok("B19", f"public Langfuse bind allowed (lab): {public_l}")
        else:
            _ok("B19", f"Langfuse UI expected on 127.0.0.1:{lf_port}")

    if include_loki:
        public_lk = check_loki_ui_binds()
        if public_lk and not allow:
            _fail("B19", f"Loki UI published publicly: {public_lk}")
        if public_lk and allow:
            _ok("B19", f"public Loki bind allowed (lab): {public_lk}")
        else:
            _ok("B19", f"Loki expected on 127.0.0.1:{_loki_port()}")

    if public and not allow:
        _fail(
            "B19",
            f"Jaeger UI :{ui_port} published on {public}",
        )
    if public and allow:
        _ok("B19", f"public Jaeger bind {public} allowed via OBS_ALLOW_PUBLIC_UI")
        return
    if binds:
        _ok("B19", f"Jaeger UI binds={binds}")
    elif duk.port_open("127.0.0.1", ui_port):
        _ok("B19", f"Jaeger UI reachable on 127.0.0.1:{ui_port}")
    else:
        _fail("B19", f"could not observe Jaeger UI bind on :{ui_port}")


def run_smoke(profile: str, *, skip_up: bool) -> None:
    load_dotenv()
    if profile not in SUPPORTED_PROFILES:
        _fail("profile", f"supported: {', '.join(SUPPORTED_PROFILES)} (got {profile})")

    want_metrics = profile in ("metrics", "full")
    want_langfuse = profile in ("langfuse", "full")
    want_loki = profile == "loki"

    report = run_preflight(profile=profile, check_ports_free=False)
    report.print()
    if not report.ok:
        _fail("preflight", "preflight failed — see checks above")

    if not skip_up:
        from argparse import Namespace

        from bootstrap_kit import cmd_up

        ok, _ = endpoints_healthy()
        brownfield = "adopt" if ok else None
        rc = cmd_up(Namespace(profile=profile, brownfield=brownfield))
        if rc != 0:
            _fail("B10/B11", f"bootstrap up exited {rc}")
        _ok("B11", "bootstrap up succeeded")

        rc2 = cmd_up(
            Namespace(
                profile=profile,
                brownfield="adopt" if endpoints_healthy()[0] else None,
            )
        )
        if rc2 != 0:
            _fail("B11", f"second bootstrap up failed with {rc2}")
        _ok("B11", "second bootstrap up ok (idempotent)")
    else:
        ok, notes = endpoints_healthy()
        if not ok:
            _fail("endpoints", "skip-up but O+J unhealthy: " + "; ".join(notes))
        for n in notes:
            _ok("endpoints", n)
        if want_metrics:
            mok, mnotes = metrics_endpoints_healthy()
            if not mok:
                _fail("endpoints", "skip-up but metrics unhealthy: " + "; ".join(mnotes))
            for n in mnotes:
                _ok("endpoints", n)
        if want_langfuse:
            lok, lnote = langfuse_ui_healthy()
            if not lok:
                _fail("endpoints", f"skip-up but langfuse unhealthy: {lnote}")
            _ok("endpoints", lnote)
        if want_loki:
            loki_h, lnotes = loki_endpoints_healthy()
            if not loki_h:
                _fail("endpoints", "skip-up but loki unhealthy: " + "; ".join(lnotes))
            for n in lnotes:
                _ok("endpoints", n)

    bind = env("OBS_UI_BIND", "127.0.0.1") or "127.0.0.1"
    detail = _jaeger_probe(bind, _base_port("jaeger_ui"))
    _ok("B17", f"Jaeger probe: {detail}")

    if want_metrics:
        try:
            t = assert_prom_targets_up()
            _ok("B14", f"Prometheus targets: {t}")
            g = assert_grafana_dashboard()
            _ok("B14", f"Grafana: {g}")
        except Exception as exc:  # noqa: BLE001
            _fail("B14", str(exc))

    if want_langfuse:
        try:
            lok, lnote = langfuse_ui_healthy()
            if not lok:
                _fail("B15", lnote)
            _ok("B15", lnote)
            for note in check_collector_langfuse_link():
                _ok("B15", note)
            ok_img, img_msg = langfuse_image_audit()
            if not ok_img:
                _fail("B20", img_msg)
            _ok("B20", img_msg)
            b18 = assert_langfuse_down_fails_smoke()
            _ok("B18", b18)
        except SmokeFailure:
            raise
        except Exception as exc:  # noqa: BLE001
            _fail("B15", str(exc))

    if want_loki:
        try:
            loki_h, lnotes = loki_endpoints_healthy()
            if not loki_h:
                _fail("B21", "Loki unhealthy: " + "; ".join(lnotes))
            probe = assert_loki_probe()
            _ok("B21", probe)
            neg = assert_loki_negative()
            _ok("B21", neg)
            graf = maybe_assert_grafana_loki_datasource()
            if graf:
                _ok("B21", graf)
            else:
                _ok("B21", "Grafana not up — Loki datasource soft-skip (co-run with metrics)")
        except SmokeFailure:
            raise
        except Exception as exc:  # noqa: BLE001
            _fail("B21", str(exc))

    if profile == "full":
        _ok("B16", "full = metrics(B14) + langfuse(B15) assertions above")

    _check_ui_binds(
        include_metrics=want_metrics,
        include_langfuse=want_langfuse,
        include_loki=want_loki,
    )

    state = BootstrapState.load()
    if state:
        _ok(
            "B8",
            f"brownfield={state.brownfield} metrics={state.metrics} "
            f"langfuse={state.langfuse} loki={state.loki}",
        )
    else:
        _ok("B8", "no state file")

    _ok("meta", f"kit root={KIT_ROOT}; loki notes: docs/zh/LOKI.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="smoke_kit_bootstrap")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--skip-up", action="store_true")
    args = parser.parse_args(argv)
    profile = profile_name(args.profile)
    try:
        run_smoke(profile, skip_up=args.skip_up)
    except SmokeFailure as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    print(f"OK  smoke_kit_bootstrap profile={profile} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
