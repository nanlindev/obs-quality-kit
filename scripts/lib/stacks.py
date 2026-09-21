"""Orchestrate sibling OTEL / Jaeger stacks for profile=base."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from . import docker_util as duk
from .compose_render import render_sibling_compose
from .paths import (
    BASE_PORTS,
    BASE_STACKS,
    RENDER_DIR,
    STACK_DEFAULTS,
    STACK_ENV_KEYS,
    STATE_FILE,
    ensure_state_dir,
    env,
    resolve_sibling,
)

BrownfieldMode = Literal["adopt", "rebind", "abort", "fresh"]


@dataclass
class StackPlan:
    name: str
    project_dir: Path
    source_compose: Path
    rendered_compose: Path
    project_name: str


@dataclass
class BootstrapState:
    profile: str
    brownfield: str
    started: list[str] = field(default_factory=list)
    adopted: list[str] = field(default_factory=list)
    rendered: dict[str, str] = field(default_factory=dict)
    bind_host: str = "127.0.0.1"
    metrics: bool = False
    langfuse: bool = False
    loki: bool = False

    def to_json(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "brownfield": self.brownfield,
            "started": self.started,
            "adopted": self.adopted,
            "rendered": self.rendered,
            "bind_host": self.bind_host,
            "metrics": self.metrics,
            "langfuse": self.langfuse,
            "loki": self.loki,
        }

    @classmethod
    def load(cls) -> BootstrapState | None:
        if not STATE_FILE.is_file():
            return None
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return cls(
            profile=data.get("profile", "base"),
            brownfield=data.get("brownfield", "fresh"),
            started=list(data.get("started") or []),
            adopted=list(data.get("adopted") or []),
            rendered=dict(data.get("rendered") or {}),
            bind_host=data.get("bind_host", "127.0.0.1"),
            metrics=bool(data.get("metrics")),
            langfuse=bool(data.get("langfuse")),
            loki=bool(data.get("loki")),
        )

    def save(self) -> None:
        ensure_state_dir()
        STATE_FILE.write_text(
            json.dumps(self.to_json(), indent=2) + "\n", encoding="utf-8"
        )


def _port(name: str) -> int:
    env_key, default = BASE_PORTS[name]
    return int(env(env_key, str(default)) or default)


def bind_host() -> str:
    return env("OBS_UI_BIND", "127.0.0.1") or "127.0.0.1"


def stack_plan(stack_name: str) -> StackPlan:
    project_dir = resolve_sibling(STACK_ENV_KEYS[stack_name], STACK_DEFAULTS[stack_name])
    source = project_dir / "docker-compose.yml"
    if not source.is_file():
        raise FileNotFoundError(f"missing compose for {stack_name}: {source}")
    ensure_state_dir()
    rendered = RENDER_DIR / f"{stack_name}.yml"
    return StackPlan(
        name=stack_name,
        project_dir=project_dir,
        source_compose=source,
        rendered_compose=rendered,
        project_name=f"obs-kit-{stack_name}",
    )


def detect_conflicts() -> dict[str, Any]:
    ports = {
        "otel_grpc": _port("otel_grpc"),
        "otel_http": _port("otel_http"),
        "jaeger_ui": _port("jaeger_ui"),
    }
    busy_ports = {k: duk.host_port_in_use(p) for k, p in ports.items()}
    containers = {
        "otel": duk.container_running_substring("otel-collector"),
        "jaeger": duk.container_running_substring("jaeger"),
    }
    return {"ports": ports, "busy_ports": busy_ports, "containers": containers}


def endpoints_healthy(*, bind: str | None = None) -> tuple[bool, list[str]]:
    host = bind or "127.0.0.1"
    notes: list[str] = []
    http_port = _port("otel_http")
    ui_port = _port("jaeger_ui")
    grpc_port = _port("otel_grpc")
    ok_http = duk.port_open(host, http_port) or duk.port_open("127.0.0.1", http_port)
    ok_grpc = duk.port_open(host, grpc_port) or duk.port_open("127.0.0.1", grpc_port)
    ok_ui = False
    ui_detail = ""
    for candidate in (host, "127.0.0.1"):
        try:
            code, _body = duk.http_get(f"http://{candidate}:{ui_port}/", timeout=3.0)
            if code < 500:
                ok_ui = True
                ui_detail = f"HTTP {code} via {candidate}"
                break
        except Exception as exc:  # noqa: BLE001 — Jaeger/ES may reset during boot
            ui_detail = str(exc)
    if ok_http:
        notes.append(f"OTLP HTTP :{http_port} open")
    else:
        notes.append(f"OTLP HTTP :{http_port} closed")
    if ok_grpc:
        notes.append(f"OTLP gRPC :{grpc_port} open")
    else:
        notes.append(f"OTLP gRPC :{grpc_port} closed")
    if ok_ui:
        notes.append(f"Jaeger UI :{ui_port} ok ({ui_detail})")
    else:
        notes.append(f"Jaeger UI :{ui_port} fail ({ui_detail})")
    return ok_http and ok_grpc and ok_ui, notes


def kit_projects_running() -> bool:
    return bool(duk.container_running_substring("obs-kit-"))


def resolve_brownfield(mode: str | None) -> BrownfieldMode:
    raw = (mode or env("OBS_BROWNFIELD", "abort") or "abort").lower()
    if raw not in ("adopt", "rebind", "abort", "fresh"):
        raise ValueError(f"invalid brownfield mode: {raw}")
    return raw  # type: ignore[return-value]


def ensure_networks() -> None:
    proxy = env("PROXY_NETWORK_NAME", "proxy_network") or "proxy_network"
    n8n_net = env("N8N_PLATFORM_NETWORK_NAME", "n8n_platform") or "n8n_platform"
    duk.ensure_network(proxy)
    duk.ensure_network(n8n_net)
    print(f"OK  networks ready: {proxy}, {n8n_net}")


def render_all(bind: str) -> list[StackPlan]:
    plans = []
    for name in BASE_STACKS:
        plan = stack_plan(name)
        render_sibling_compose(plan.source_compose, plan.rendered_compose, bind_host=bind)
        plans.append(plan)
        print(f"OK  rendered {plan.rendered_compose} (bind={bind})")
    return plans


def start_stacks(plans: list[StackPlan]) -> None:
    for plan in plans:
        print(f"→  compose up {plan.name} (project={plan.project_name})")
        duk.compose_up(
            project_dir=plan.project_dir,
            compose_file=plan.rendered_compose,
            project_name=plan.project_name,
        )
        print(f"OK  started {plan.name}")


def stop_stacks(plans: list[StackPlan], *, volumes: bool = False) -> None:
    for plan in plans:
        print(f"→  compose down {plan.name} (project={plan.project_name})")
        duk.compose_down(
            project_dir=plan.project_dir,
            compose_file=plan.rendered_compose,
            project_name=plan.project_name,
            volumes=volumes,
        )
        print(f"OK  stopped {plan.name}")


def wait_healthy(timeout_s: int = 180) -> None:
    deadline = time.time() + timeout_s
    last: list[str] = []
    while time.time() < deadline:
        try:
            ok, last = endpoints_healthy()
        except Exception as exc:  # noqa: BLE001
            last = [f"probe error: {exc}"]
            ok = False
        if ok:
            for line in last:
                print(f"OK  {line}")
            return
        time.sleep(3)
    raise RuntimeError("timeout waiting for O+J endpoints:\n  " + "\n  ".join(last))


def cleanup_hint() -> str:
    return (
        "Partial failure cleanup:\n"
        "  ./scripts/bootstrap.sh down --profile base\n"
        "  # force stop kit-started projects even if state says adopted:\n"
        "  ./scripts/bootstrap.sh down --profile base --force\n"
        f"  # state file: {STATE_FILE}"
    )
