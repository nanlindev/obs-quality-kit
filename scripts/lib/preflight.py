"""Preflight checks for kit bootstrap (PRD §16.2 B1–B7, B9, B19–B20 fragments)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import docker_util as duk
from .compose_render import assert_no_latest, images_from_compose_text
from .paths import (
    BASE_PORTS,
    LOKI_PORTS,
    METRICS_PORTS,
    ROOT,
    STACK_DEFAULTS,
    STACK_ENV_KEYS,
    env,
    resolve_sibling,
)


@dataclass
class CheckResult:
    code: str  # e.g. B1
    ok: bool
    message: str
    blocking: bool = True


@dataclass
class PreflightReport:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok or not c.blocking for c in self.checks)

    def add(self, check: CheckResult) -> None:
        self.checks.append(check)

    def print(self) -> None:
        for c in self.checks:
            flag = "OK " if c.ok else ("FAIL" if c.blocking else "WARN")
            print(f"{flag}  [{c.code}] {c.message}")


def _port(name: str) -> int:
    env_key, default = BASE_PORTS[name]
    raw = env(env_key, str(default))
    return int(raw or default)


def _metrics_port(name: str) -> int:
    env_key, default = METRICS_PORTS[name]
    raw = env(env_key, str(default))
    return int(raw or default)


def _loki_port() -> int:
    env_key, default = LOKI_PORTS["loki"]
    raw = env(env_key, str(default))
    return int(raw or default)


def min_compose_version() -> tuple[int, int, int]:
    return (2, 20, 0)


def run_preflight(
    *,
    profile: str = "base",
    check_ports_free: bool = False,
    sibling_compose_files: list[Path] | None = None,
) -> PreflightReport:
    """Run automated preflight. Does not pull images (B9)."""
    report = PreflightReport()

    # B1 daemon
    ok, msg = duk.daemon_ok()
    report.add(CheckResult("B1", ok, msg))
    if not ok:
        return report

    # B2 compose version
    ver_text, ver = duk.compose_version()
    min_v = min_compose_version()
    if ver is None:
        report.add(
            CheckResult(
                "B2",
                False,
                f"could not parse Compose version from: {ver_text!r} (need >= {min_v[0]}.{min_v[1]}.{min_v[2]})",
            )
        )
    else:
        ok_v = ver >= min_v
        report.add(
            CheckResult(
                "B2",
                ok_v,
                f"Compose {ver_text} (minimum {min_v[0]}.{min_v[1]}.{min_v[2]})",
            )
        )

    # B3 permissions — light probe: can we run docker ps?
    ps = duk.run(["docker", "ps"], timeout=30)
    if ps.ok:
        b3_msg = "docker ps ok"
    else:
        err_lines = (ps.stderr or ps.stdout or "").strip().splitlines()
        b3_msg = f"permission or docker error: {err_lines[-1] if err_lines else 'unknown'}"
    report.add(CheckResult("B3", ps.ok, b3_msg))

    # B4 disk (+ stronger thresholds for langfuse/full — Review-3)
    free = duk.disk_free_gib(ROOT)
    min_gib = float(env("OBS_DISK_MIN_GIB", "2") or "2")
    warn_gib = float(env("OBS_DISK_WARN_GIB", "5") or "5")
    if profile in ("langfuse", "full"):
        min_gib = max(min_gib, float(env("OBS_DISK_MIN_GIB_LANGFUSE", "4") or "4"))
        warn_gib = max(warn_gib, float(env("OBS_DISK_WARN_GIB_LANGFUSE", "10") or "10"))
    if profile == "loki":
        min_gib = max(min_gib, float(env("OBS_DISK_MIN_GIB_LOKI", "3") or "3"))
        warn_gib = max(warn_gib, float(env("OBS_DISK_WARN_GIB_LOKI", "8") or "8"))
    if free < min_gib:
        report.add(
            CheckResult(
                "B4",
                False,
                f"free disk {free:.1f} GiB < minimum {min_gib} GiB for profile={profile}",
            )
        )
    elif free < warn_gib:
        report.add(
            CheckResult(
                "B4",
                True,
                f"free disk {free:.1f} GiB < warn {warn_gib} GiB "
                f"(profile={profile}; avoid long-term full/Langfuse/Loki+full on tiny disks)",
                blocking=False,
            )
        )
    else:
        report.add(CheckResult("B4", True, f"free disk {free:.1f} GiB"))

    # Review-3 memory soft warning for full; Review-P2-4 for loki co-run with full
    mem = duk.host_mem_gib()
    if mem is not None:
        if profile == "full" and mem < 8.0:
            report.add(
                CheckResult(
                    "B4m",
                    True,
                    f"host RAM ~{mem:.1f} GiB < 8 GiB — do not leave profile=full running long-term",
                    blocking=False,
                )
            )
        elif profile == "loki" and mem < 8.0:
            report.add(
                CheckResult(
                    "B4m",
                    True,
                    f"host RAM ~{mem:.1f} GiB — do not co-run loki with full long-term on ≤8GB",
                    blocking=False,
                )
            )
        else:
            report.add(
                CheckResult("B4m", True, f"host RAM ~{mem:.1f} GiB", blocking=False)
            )

    # B6 / B7 networks
    proxy = env("PROXY_NETWORK_NAME", "proxy_network") or "proxy_network"
    n8n_net = env("N8N_PLATFORM_NETWORK_NAME", "n8n_platform") or "n8n_platform"
    if duk.network_exists(proxy):
        report.add(CheckResult("B6", True, f"network {proxy} exists"))
    else:
        report.add(
            CheckResult(
                "B6",
                True,
                f"network {proxy} missing (bootstrap will create; strategy=create-or-abort)",
                blocking=False,
            )
        )
    report.add(
        CheckResult(
            "B7",
            True,
            f"network names fixed to {proxy!r} / {n8n_net!r} (no silent rename)",
        )
    )

    # B5 ports
    ports = {
        "otel_grpc": _port("otel_grpc"),
        "otel_http": _port("otel_http"),
        "jaeger_ui": _port("jaeger_ui"),
    }
    if profile in ("metrics", "full"):
        ports.update(
            {
                "prometheus": _metrics_port("prometheus"),
                "grafana": _metrics_port("grafana"),
                "cadvisor": _metrics_port("cadvisor"),
            }
        )
    if profile in ("langfuse", "full"):
        from .paths import LANGFUSE_PORTS

        for name, (key, default) in LANGFUSE_PORTS.items():
            ports[name] = int(env(key, str(default)) or default)
    if profile == "loki":
        ports["loki"] = _loki_port()
    busy = {k: duk.host_port_in_use(p) for k, p in ports.items()}
    busy_list = [f"{k}={ports[k]}" for k, used in busy.items() if used]
    if check_ports_free and busy_list:
        report.add(
            CheckResult(
                "B5",
                False,
                f"ports in use (fresh start blocked): {', '.join(busy_list)} — use --brownfield adopt|rebind|abort",
            )
        )
    else:
        report.add(
            CheckResult(
                "B5",
                True,
                "ports: "
                + ", ".join(
                    f"{k}:{ports[k]}={'busy' if busy[k] else 'free'}" for k in ports
                ),
            )
        )

    # B20 image pins
    files = sibling_compose_files
    if files is None:
        files = []
        if profile in ("base", "metrics", "langfuse", "full", "loki"):
            for stack in ("otel-collector-stack", "jaeger-stack"):
                path = resolve_sibling(STACK_ENV_KEYS[stack], STACK_DEFAULTS[stack])
                compose = path / "docker-compose.yml"
                if compose.is_file():
                    files.append(compose)
        if profile in ("metrics", "full"):
            metrics_compose = ROOT / "profiles" / "metrics" / "compose.yml"
            files.append(metrics_compose)
        if profile == "loki":
            files.append(ROOT / "profiles" / "loki" / "compose.yml")
        # langfuse sibling has floating/untagged images; kit render pins ClickHouse.
        # Preflight only notes sibling path exists (hard pin audit runs on rendered file in smoke).
        if profile in ("langfuse", "full"):
            lf = resolve_sibling(STACK_ENV_KEYS["langfuse-stack"], STACK_DEFAULTS["langfuse-stack"])
            lf_compose = lf / "docker-compose.yml"
            if not lf_compose.is_file():
                report.add(CheckResult("B20", False, f"langfuse compose missing: {lf_compose}"))
            else:
                report.add(
                    CheckResult(
                        "B20l",
                        True,
                        f"langfuse sibling compose present ({lf_compose}); "
                        "kit render applies ClickHouse pin + port remap",
                        blocking=False,
                    )
                )
    bad: list[str] = []
    scanned = 0
    for compose in files or []:
        if not compose.is_file():
            report.add(
                CheckResult("B20", False, f"compose missing for pin audit: {compose}")
            )
            continue
        images = images_from_compose_text(compose.read_text(encoding="utf-8"))
        scanned += len(images)
        bad.extend(assert_no_latest(images))
    if bad:
        report.add(
            CheckResult(
                "B20",
                False,
                f"unpinned or :latest images: {', '.join(bad)}",
            )
        )
    else:
        report.add(
            CheckResult(
                "B20",
                True,
                f"image pins ok ({scanned} refs scanned for profile={profile})",
            )
        )

    # B9 marker — structural: preflight never invokes pull
    report.add(
        CheckResult(
            "B9",
            True,
            "preflight completed without image pull (pull only after preflight passes in bootstrap up)",
        )
    )

    return report
