"""Kit-owned Loki + Promtail stack (profile: loki)."""

from __future__ import annotations

import json
import time
from urllib import error, request

from . import docker_util as duk
from .paths import LOKI_PORTS, ROOT, env


def _port() -> int:
    key, default = LOKI_PORTS["loki"]
    return int(env(key, str(default)) or default)


def bind_host() -> str:
    return env("OBS_UI_BIND", "127.0.0.1") or "127.0.0.1"


def loki_project_name() -> str:
    """Dedicated compose project — must not share with metrics (orphan up would delete siblings)."""
    base = env("COMPOSE_PROJECT_NAME", "obs-quality-kit") or "obs-quality-kit"
    return f"{base}-loki"


def _legacy_shared_project() -> str:
    return env("COMPOSE_PROJECT_NAME", "obs-quality-kit") or "obs-quality-kit"


def _retire_legacy_loki_project() -> None:
    """Stop Loki services still running under the old shared project (port reuse)."""
    legacy = _legacy_shared_project()
    if legacy == loki_project_name():
        return
    args = [
        "docker",
        "compose",
        "-f",
        str(ROOT / "profiles" / "loki" / "compose.yml"),
        "--profile",
        "loki",
        "-p",
        legacy,
        "down",
    ]
    print(f"→  retire legacy loki project={legacy} (no volumes)")
    try:
        duk.run(args, check=False, timeout=300, cwd=ROOT)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN  legacy loki retire skipped: {exc}")


def loki_compose_args() -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        str(ROOT / "profiles" / "loki" / "compose.yml"),
        "--profile",
        "loki",
        "-p",
        loki_project_name(),
    ]


def start_loki() -> None:
    import os

    os.environ.setdefault("OBS_UI_BIND", bind_host())
    _retire_legacy_loki_project()
    # Never --remove-orphans: co-run with metrics must not delete grafana/prometheus.
    print(f"→  compose up loki (project={loki_project_name()})")
    duk.run(
        loki_compose_args() + ["up", "-d"],
        check=True,
        timeout=600,
        cwd=ROOT,
    )
    print("OK  loki stack started")


def stop_loki(*, volumes: bool = False) -> None:
    # Never --remove-orphans across addon projects.
    _retire_legacy_loki_project()
    args = loki_compose_args() + ["down"]
    if volumes:
        args.append("-v")
    print(f"→  compose down loki (project={loki_project_name()})")
    duk.run(args, check=True, timeout=300, cwd=ROOT)
    print("OK  loki stack stopped")


def _opener():
    return request.build_opener(request.ProxyHandler({}))


def loki_base_url() -> str:
    return f"http://127.0.0.1:{_port()}"


def loki_endpoints_healthy() -> tuple[bool, list[str]]:
    notes: list[str] = []
    port = _port()
    open_ok = duk.port_open("127.0.0.1", port) or duk.port_open(bind_host(), port)
    notes.append(f"Loki :{port}={'open' if open_ok else 'closed'}")
    if not open_ok:
        return False, notes
    try:
        code, body = duk.http_get(f"{loki_base_url()}/ready", timeout=3.0)
        ready = code == 200 and "ready" in (body or "").lower()
        notes.append(f"Loki /ready HTTP {code}")
        return ready, notes
    except Exception as exc:  # noqa: BLE001
        notes.append(str(exc))
        return False, notes


def wait_loki_healthy(timeout_s: int = 180) -> None:
    deadline = time.time() + timeout_s
    last: list[str] = []
    while time.time() < deadline:
        ok, last = loki_endpoints_healthy()
        if ok:
            for line in last:
                print(f"OK  {line}")
            return
        time.sleep(3)
    raise RuntimeError("timeout waiting for Loki:\n  " + "\n  ".join(last))


def push_probe_log(marker: str) -> None:
    """Push one labeled log line via Loki HTTP API (smoke probe; no Promtail required)."""
    now_ns = str(int(time.time() * 1e9))
    payload = {
        "streams": [
            {
                "stream": {"job": "obs-kit-smoke", "probe": "loki"},
                "values": [[now_ns, marker]],
            }
        ]
    }
    data = json.dumps(payload).encode()
    req = request.Request(
        f"{loki_base_url()}/loki/api/v1/push",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _opener().open(req, timeout=10) as resp:
            if resp.getcode() not in (200, 204):
                raise RuntimeError(f"Loki push HTTP {resp.getcode()}")
    except error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        raise RuntimeError(f"Loki push HTTP {exc.code}: {body}") from exc


def query_has_marker(marker: str, *, wait_s: float = 15.0) -> bool:
    deadline = time.time() + wait_s
    # LogQL: exact line filter on smoke job
    query = '{job="obs-kit-smoke"} |= "' + marker.replace('"', "") + '"'
    from urllib.parse import urlencode

    last_err = ""
    while time.time() < deadline:
        qs = urlencode({"query": query, "limit": "20"})
        url = f"{loki_base_url()}/loki/api/v1/query_range?{qs}"
        # query_range needs start/end
        end_ns = int(time.time() * 1e9)
        start_ns = end_ns - int(300 * 1e9)
        qs = urlencode(
            {
                "query": query,
                "limit": "20",
                "start": str(start_ns),
                "end": str(end_ns),
            }
        )
        url = f"{loki_base_url()}/loki/api/v1/query_range?{qs}"
        try:
            code, body = duk.http_get(url, timeout=8.0)
            if code != 200:
                last_err = f"HTTP {code} {body[:200]}"
            else:
                data = json.loads(body or "{}")
                results = ((data.get("data") or {}).get("result")) or []
                blob = json.dumps(results)
                if marker in blob:
                    return True
                last_err = f"no marker in {len(results)} streams"
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
        time.sleep(0.5)
    if last_err:
        raise RuntimeError(f"Loki query miss for marker={marker!r}: {last_err}")
    return False


def assert_loki_probe() -> str:
    """B21: push + query round-trip (readable log line)."""
    marker = f"obs-kit-loki-probe-{int(time.time())}"
    push_probe_log(marker)
    if not query_has_marker(marker, wait_s=20.0):
        raise RuntimeError(f"Loki did not return probe marker {marker}")
    return f"push+query ok marker={marker}"


def assert_loki_negative() -> str:
    """Negative: query for impossible marker → empty / readable miss."""
    marker = "obs-kit-loki-never-" + ("0" * 24)
    from urllib.parse import urlencode

    end_ns = int(time.time() * 1e9)
    start_ns = end_ns - int(60 * 1e9)
    qs = urlencode(
        {
            "query": '{job="obs-kit-smoke"} |= "' + marker + '"',
            "limit": "5",
            "start": str(start_ns),
            "end": str(end_ns),
        }
    )
    url = f"{loki_base_url()}/loki/api/v1/query_range?{qs}"
    code, body = duk.http_get(url, timeout=8.0)
    if code != 200:
        raise RuntimeError(f"negative query HTTP {code}: {body[:200]}")
    data = json.loads(body or "{}")
    results = ((data.get("data") or {}).get("result")) or []
    if results:
        raise RuntimeError("negative query unexpectedly returned streams")
    return "fake marker → empty Loki result (readable miss)"


def check_loki_ui_binds() -> list[str]:
    public: list[str] = []
    port = _port()
    for b in duk.list_listening_binds(port):
        if b in ("0.0.0.0", "::", "[::]"):
            public.append(f"loki:{port}->{b}")
    return public


def maybe_assert_grafana_loki_datasource() -> str | None:
    """Soft: if Grafana is up, expect Loki datasource provisioned."""
    from . import metrics as metrics_mod

    graf = metrics_mod._port("grafana")
    if not duk.port_open("127.0.0.1", graf):
        return None
    user = env("GRAFANA_ADMIN_USER", "admin") or "admin"
    password = metrics_mod.ensure_grafana_password()
    base = f"http://127.0.0.1:{graf}"
    ds = metrics_mod._http_json(f"{base}/api/datasources", auth=(user, password))
    if not isinstance(ds, list):
        raise RuntimeError(f"Grafana datasources unexpected: {ds!r}")
    if not any(d.get("type") == "loki" for d in ds):
        raise RuntimeError(
            "Grafana up but Loki datasource missing "
            "(restart metrics after P2-4 provisioning change)"
        )
    return "Grafana has Loki datasource"
