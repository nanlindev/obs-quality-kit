"""Paths and .env loading for obs-quality-kit scripts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / ".obs-kit"
STATE_FILE = STATE_DIR / "state.json"
RENDER_DIR = STATE_DIR / "rendered"


def load_dotenv(path: Path | None = None) -> dict[str, str]:
    """Load KEY=VALUE into os.environ (setdefault). Returns loaded pairs."""
    env_path = path or (ROOT / ".env")
    loaded: dict[str, str] = {}
    if not env_path.is_file():
        example = ROOT / ".env.example"
        if example.is_file():
            env_path = example
        else:
            return loaded
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
        loaded[key] = value
    return loaded


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def resolve_sibling(env_key: str, default_rel: str) -> Path:
    raw = env(env_key, default_rel)
    path = Path(raw)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)


def profile_name(cli_profile: str | None = None) -> str:
    return (cli_profile or env("OBS_KIT_PROFILE", "base") or "base").lower()


BASE_STACKS = ("otel-collector-stack", "jaeger-stack")

STACK_ENV_KEYS: Mapping[str, str] = {
    "otel-collector-stack": "OTEL_STACK_PATH",
    "jaeger-stack": "JAEGER_STACK_PATH",
    "langfuse-stack": "LANGFUSE_STACK_PATH",
}

STACK_DEFAULTS: Mapping[str, str] = {
    "otel-collector-stack": "../otel-collector-stack",
    "jaeger-stack": "../jaeger-stack",
    "langfuse-stack": "../langfuse-stack",
}

# Host ports checked / rewritten for base profile
BASE_PORTS = {
    "otel_grpc": ("OBS_OTEL_GRPC_PORT", 4317),
    "otel_http": ("OBS_OTEL_HTTP_PORT", 4318),
    "jaeger_ui": ("OBS_JAEGER_UI_PORT", 16686),
}

# Kit-owned metrics profile host ports (Grafana avoids Langfuse :3000)
METRICS_PORTS = {
    "prometheus": ("OBS_PROMETHEUS_PORT", 9090),
    "grafana": ("OBS_GRAFANA_PORT", 3001),
    "cadvisor": ("OBS_CADVISOR_PORT", 8088),
}

# Kit-owned Loki profile host port
LOKI_PORTS = {
    "loki": ("OBS_LOKI_PORT", 3100),
}

SUPPORTED_PROFILES = ("base", "metrics", "langfuse", "full", "loki")

# Langfuse host ports after kit remap (avoid Grafana :3001 / Prometheus :9090)
LANGFUSE_PORTS = {
    "langfuse_ui": ("OBS_LANGFUSE_UI_PORT", 3000),
    "langfuse_minio_api": ("OBS_LANGFUSE_MINIO_API_PORT", 9092),
}
