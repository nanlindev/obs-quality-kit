"""Kit-owned metrics stack (Prometheus + Grafana + cAdvisor)."""

from __future__ import annotations

import json
import secrets
import string
import time
from urllib import request

from . import docker_util as duk
from .paths import (
    METRICS_PORTS,
    ROOT,
    STATE_DIR,
    ensure_state_dir,
    env,
)

GRAFANA_PASS_FILE = STATE_DIR / "grafana_admin_password.txt"
DASHBOARD_UID = "obs-kit-infra"


def _port(name: str) -> int:
    key, default = METRICS_PORTS[name]
    return int(env(key, str(default)) or default)


def bind_host() -> str:
    return env("OBS_UI_BIND", "127.0.0.1") or "127.0.0.1"


def ensure_grafana_password() -> str:
    """Return admin password; generate + persist if unset (never commit)."""
    existing = env("GRAFANA_ADMIN_PASSWORD", "")
    if existing:
        return existing
    ensure_state_dir()
    if GRAFANA_PASS_FILE.is_file():
        pw = GRAFANA_PASS_FILE.read_text(encoding="utf-8").strip()
        if pw:
            os_environ_set("GRAFANA_ADMIN_PASSWORD", pw)
            return pw
    alphabet = string.ascii_letters + string.digits
    pw = "gk_" + "".join(secrets.choice(alphabet) for _ in range(20))
    GRAFANA_PASS_FILE.write_text(pw + "\n", encoding="utf-8")
    os_environ_set("GRAFANA_ADMIN_PASSWORD", pw)
    print(f"OK  generated GRAFANA_ADMIN_PASSWORD → {GRAFANA_PASS_FILE}")
    return pw


def os_environ_set(key: str, value: str) -> None:
    import os

    os.environ[key] = value


def metrics_project_name() -> str:
    """Dedicated compose project — must not share with loki (orphan up would delete siblings)."""
    base = env("COMPOSE_PROJECT_NAME", "obs-quality-kit") or "obs-quality-kit"
    return f"{base}-metrics"


def _legacy_shared_project() -> str:
    """Pre-split project name that hosted both metrics and loki (unsafe with --remove-orphans)."""
    return env("COMPOSE_PROJECT_NAME", "obs-quality-kit") or "obs-quality-kit"


def _retire_legacy_metrics_project() -> None:
    """Stop metrics services still running under the old shared project (port reuse)."""
    legacy = _legacy_shared_project()
    if legacy == metrics_project_name():
        return
    args = [
        "docker",
        "compose",
        "-f",
        str(ROOT / "profiles" / "metrics" / "compose.yml"),
        "--profile",
        "metrics",
        "-p",
        legacy,
        "down",
    ]
    print(f"→  retire legacy metrics project={legacy} (no volumes)")
    try:
        duk.run(args, check=False, timeout=300, cwd=ROOT)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN  legacy metrics retire skipped: {exc}")


def metrics_compose_args() -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        str(ROOT / "profiles" / "metrics" / "compose.yml"),
        "--profile",
        "metrics",
        "-p",
        metrics_project_name(),
    ]


def start_metrics() -> None:
    ensure_grafana_password()
    import os

    os.environ.setdefault("OBS_UI_BIND", bind_host())
    _retire_legacy_metrics_project()
    # Never --remove-orphans: shared-host co-run with loki / other kit projects.
    print(f"→  compose up metrics (project={metrics_project_name()})")
    duk.run(
        metrics_compose_args() + ["up", "-d"],
        check=True,
        timeout=600,
        cwd=ROOT,
    )
    print("OK  metrics stack started")


def stop_metrics(*, volumes: bool = False) -> None:
    # Never --remove-orphans: would delete co-running loki containers if projects were shared.
    _retire_legacy_metrics_project()
    args = metrics_compose_args() + ["down"]
    if volumes:
        args.append("-v")
    print(f"→  compose down metrics (project={metrics_project_name()})")
    duk.run(args, check=True, timeout=300, cwd=ROOT)
    print("OK  metrics stack stopped")


def _http_json(url: str, *, auth: tuple[str, str] | None = None, timeout: float = 8.0) -> object:
    headers = {"Accept": "application/json"}
    req = request.Request(url, headers=headers, method="GET")
    if auth:
        import base64

        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    opener = request.build_opener(request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def metrics_endpoints_healthy() -> tuple[bool, list[str]]:
    host = bind_host()
    notes: list[str] = []
    prom = _port("prometheus")
    graf = _port("grafana")
    cad = _port("cadvisor")

    ok_prom = duk.port_open("127.0.0.1", prom) or duk.port_open(host, prom)
    ok_graf = duk.port_open("127.0.0.1", graf) or duk.port_open(host, graf)
    ok_cad = duk.port_open("127.0.0.1", cad) or duk.port_open(host, cad)
    notes.append(f"Prometheus :{prom}={'open' if ok_prom else 'closed'}")
    notes.append(f"Grafana :{graf}={'open' if ok_graf else 'closed'}")
    notes.append(f"cAdvisor :{cad}={'open' if ok_cad else 'closed'}")
    return ok_prom and ok_graf and ok_cad, notes


def wait_metrics_healthy(timeout_s: int = 180) -> None:
    deadline = time.time() + timeout_s
    last: list[str] = []
    while time.time() < deadline:
        ok, last = metrics_endpoints_healthy()
        if ok:
            # Also require Prometheus /-/ready
            try:
                code, _ = duk.http_get(f"http://127.0.0.1:{_port('prometheus')}/-/ready", timeout=3.0)
                if code == 200:
                    for line in last:
                        print(f"OK  {line}")
                    return
                last.append(f"Prometheus ready HTTP {code}")
            except Exception as exc:  # noqa: BLE001
                last.append(str(exc))
        time.sleep(3)
    raise RuntimeError("timeout waiting for metrics endpoints:\n  " + "\n  ".join(last))


def assert_prom_targets_up(*, retries: int = 20, delay_s: float = 3.0) -> str:
    """B14: at least one active target must be up (cadvisor and/or prometheus)."""
    url = f"http://127.0.0.1:{_port('prometheus')}/api/v1/targets"
    last_err = "no attempt"
    for _ in range(retries):
        try:
            data = _http_json(url)
            if not isinstance(data, dict) or data.get("status") != "success":
                last_err = f"unexpected Prometheus targets payload: {data!r}"
            else:
                active = (data.get("data") or {}).get("activeTargets") or []
                up = [t for t in active if t.get("health") == "up"]
                if up:
                    summary = ", ".join(
                        f"{t.get('labels', {}).get('job')}:{t.get('labels', {}).get('instance')}"
                        for t in up
                    )
                    return f"{len(up)} up ({summary})"
                jobs = [f"{t.get('labels', {}).get('job')}={t.get('health')}" for t in active]
                last_err = f"no Prometheus targets up; active={jobs}"
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
        time.sleep(delay_s)
    raise RuntimeError(last_err)


def assert_grafana_dashboard() -> str:
    """B14: datasource + provisioned infra dashboard present; optional query has series."""
    user = env("GRAFANA_ADMIN_USER", "admin") or "admin"
    password = ensure_grafana_password()
    base = f"http://127.0.0.1:{_port('grafana')}"
    auth = (user, password)

    ds = _http_json(f"{base}/api/datasources", auth=auth)
    if not isinstance(ds, list) or not any(d.get("type") == "prometheus" for d in ds):
        raise RuntimeError(f"Grafana missing Prometheus datasource: {ds!r}")

    dash = _http_json(f"{base}/api/dashboards/uid/{DASHBOARD_UID}", auth=auth)
    if not isinstance(dash, dict) or "dashboard" not in dash:
        raise RuntimeError(f"Grafana dashboard uid={DASHBOARD_UID} missing: {dash!r}")

    # Query via Grafana datasource proxy — proves wiring has data path
    # Prefer Prometheus query_range for up
    try:
        qurl = (
            f"http://127.0.0.1:{_port('prometheus')}/api/v1/query"
            f"?query=up"
        )
        q = _http_json(qurl)
        result = ((q or {}).get("data") or {}).get("result") or []
        if not result:
            raise RuntimeError("Prometheus query up returned no series")
        return f"datasource ok; dashboard {DASHBOARD_UID}; up series={len(result)}"
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Grafana/Prom data check failed: {exc}") from exc


def check_metrics_ui_binds() -> list[str]:
    """Return public binds for Grafana/Prom/cAdvisor host ports (B19)."""
    public: list[str] = []
    for name in METRICS_PORTS:
        port = _port(name)
        for b in duk.list_listening_binds(port):
            if b in ("0.0.0.0", "::", "[::]"):
                public.append(f"{name}:{port}->{b}")
    return public
