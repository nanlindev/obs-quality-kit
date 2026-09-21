"""Orchestrate sibling langfuse-stack for kit profiles langfuse/full."""

from __future__ import annotations

import json
import re
import secrets
import string
import time
from pathlib import Path
from urllib import error, request

from . import docker_util as duk
from .compose_render import assert_no_latest, images_from_compose_text, rewrite_publish_bind
from .paths import (
    RENDER_DIR,
    ROOT,
    STACK_DEFAULTS,
    STACK_ENV_KEYS,
    STATE_DIR,
    ensure_state_dir,
    env,
    resolve_sibling,
)

WEAK_NEXTAUTH = {"", "mysecret", "changeme", "secret"}
WEAK_SALT = {"", "mysalt", "changeme", "salt"}

# Floating/untagged images in sibling langfuse-stack → pin in kit-rendered compose (P2-1).
# langfuse:3 / :3.225 must NOT be used — Hub briefly served v4 under those tags (2026-09).
IMAGE_PIN_REWRITES = {
    "docker.io/clickhouse/clickhouse-server": "docker.io/clickhouse/clickhouse-server:24.8",
    "clickhouse/clickhouse-server": "clickhouse/clickhouse-server:24.8",
    "cgr.dev/chainguard/minio": (
        "cgr.dev/chainguard/minio@sha256:"
        "29bbe439d3a3c41afac869973c08a70b1a7e7e6a3822015a110bf53df7e3e66c"
    ),
    "docker.io/langfuse/langfuse:3": "docker.io/langfuse/langfuse:3.225.5",
    "docker.io/langfuse/langfuse-worker:3": "docker.io/langfuse/langfuse-worker:3.225.5",
    "langfuse/langfuse:3": "docker.io/langfuse/langfuse:3.225.5",
    "langfuse/langfuse-worker:3": "docker.io/langfuse/langfuse-worker:3.225.5",
    "docker.io/redis:7": "docker.io/redis:7.4.2",
    "redis:7": "docker.io/redis:7.4.2",
}

_POSTGRES_IMAGE_RE = re.compile(
    r"^(\s*image:\s*)docker\.io/postgres:\$\{POSTGRES_VERSION:-[^}]+\}\s*$",
    flags=re.MULTILINE,
)
POSTGRES_PIN = "docker.io/postgres:17.5"


def langfuse_ui_port() -> int:
    return int(env("OBS_LANGFUSE_UI_PORT", "3000") or "3000")


def langfuse_minio_api_port() -> int:
    return int(env("OBS_LANGFUSE_MINIO_API_PORT", "9092") or "9092")


def bind_host() -> str:
    return env("OBS_UI_BIND", "127.0.0.1") or "127.0.0.1"


def langfuse_dir() -> Path:
    return resolve_sibling(STACK_ENV_KEYS["langfuse-stack"], STACK_DEFAULTS["langfuse-stack"])


def rendered_compose_path() -> Path:
    ensure_state_dir()
    return RENDER_DIR / "langfuse-stack.yml"


def project_name() -> str:
    return "obs-kit-langfuse-stack"


def _gen_secret(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def ensure_langfuse_secrets() -> dict[str, str]:
    """Force non-default NEXTAUTH_SECRET / SALT (Review-3). Persist under .obs-kit/."""
    ensure_state_dir()
    secrets_file = STATE_DIR / "langfuse_secrets.json"
    data: dict[str, str] = {}
    if secrets_file.is_file():
        try:
            data = json.loads(secrets_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}

    sibling_env = langfuse_dir() / ".env"
    sibling: dict[str, str] = {}
    if sibling_env.is_file():
        for raw in sibling_env.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            sibling[k.strip()] = v.strip().strip('"').strip("'")

    nextauth = (
        env("NEXTAUTH_SECRET", "")
        or data.get("NEXTAUTH_SECRET", "")
        or sibling.get("NEXTAUTH_SECRET", "")
    )
    salt = env("SALT", "") or data.get("SALT", "") or sibling.get("SALT", "")

    changed = False
    if nextauth.strip() in WEAK_NEXTAUTH:
        nextauth = _gen_secret(32)
        changed = True
        print("OK  generated strong NEXTAUTH_SECRET (was weak/default)")
    if salt.strip() in WEAK_SALT:
        salt = "lf_" + "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(24)
        )
        changed = True
        print("OK  generated strong SALT (was weak/default)")

    data = {
        "NEXTAUTH_SECRET": nextauth,
        "SALT": salt,
        "NEXTAUTH_URL": f"http://localhost:{langfuse_ui_port()}",
    }
    secrets_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if changed:
        print(f"OK  langfuse secrets → {secrets_file}")

    import os

    for k, v in data.items():
        os.environ[k] = v
    return data


def _pin_images(text: str) -> str:
    out = text
    for old, new in IMAGE_PIN_REWRITES.items():
        out = re.sub(
            rf"(^\s*image:\s*){re.escape(old)}\s*$",
            rf"\1{new}",
            out,
            flags=re.MULTILINE,
        )
    out = _POSTGRES_IMAGE_RE.sub(rf"\1{POSTGRES_PIN}", out)
    return out


def _floating_major_tags(images: list[str]) -> list[str]:
    """Tags that are major-only (e.g. :3, :7) — not acceptable after P2-1."""
    bad: list[str] = []
    for image in images:
        if "@sha256:" in image:
            continue
        name = image.split("/")[-1]
        if ":" not in name:
            continue
        tag = name.rsplit(":", 1)[-1]
        if re.fullmatch(r"\d+", tag):
            bad.append(image)
    return bad


def _remap_host_ports(text: str, port_map: dict[int, int]) -> str:
    """Rewrite host publish port (left side) when it matches port_map keys."""

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        host = match.group("host")
        pub = int(match.group("pub"))
        tgt = match.group("tgt")
        proto = match.group("proto")
        suffix = f"/{proto}" if proto else ""
        new_pub = port_map.get(pub, pub)
        host_part = f"{host}:" if host else ""
        # Always emit quoted form after remap
        bind = host or bind_host()
        return f'{indent}"{bind}:{new_pub}:{tgt}{suffix}"'

    return re.sub(
        r"""^(\s*-\s*)['"]?"""
        r"(?:(?P<host>\d+\.\d+\.\d+\.\d+|\[::\]|::|localhost):)?"
        r"(?P<pub>\d+):(?P<tgt>\d+)"
        r"""(?:/(?P<proto>tcp|udp))?['"]?\s*(?:#.*)?$""",
        repl,
        text,
        flags=re.MULTILINE,
    )


def render_langfuse_compose() -> Path:
    source = langfuse_dir() / "docker-compose.yml"
    if not source.is_file():
        raise FileNotFoundError(f"missing langfuse compose: {source}")
    secrets = ensure_langfuse_secrets()
    text = source.read_text(encoding="utf-8")
    text = rewrite_publish_bind(text, bind_host())
    # Remap conflicts with kit metrics (Grafana:3001, Prometheus:9090)
    text = _remap_host_ports(
        text,
        {
            3001: langfuse_ui_port(),
            9090: langfuse_minio_api_port(),
        },
    )
    text = _pin_images(text)
    # Force NEXTAUTH_URL default in compose text for browser login
    text = re.sub(
        r"(NEXTAUTH_URL:\s*\$\{NEXTAUTH_URL:-)[^}]+(\})",
        rf"\1{secrets['NEXTAUTH_URL']}\2",
        text,
    )
    dest = rendered_compose_path()
    dest.write_text(text, encoding="utf-8")
    print(
        f"OK  rendered {dest} "
        f"(UI :{langfuse_ui_port()}, minio API :{langfuse_minio_api_port()}, bind={bind_host()})"
    )
    return dest


def start_langfuse() -> None:
    secrets = ensure_langfuse_secrets()
    compose = render_langfuse_compose()
    project_dir = langfuse_dir()
    # Merge env for compose variable substitution
    import os

    for k, v in secrets.items():
        os.environ[k] = v
    print(f"→  compose up langfuse-stack (project={project_name()})")
    duk.compose_up(
        project_dir=project_dir,
        compose_file=compose,
        project_name=project_name(),
    )
    print("OK  started langfuse-stack")


def stop_langfuse(*, volumes: bool = False) -> None:
    compose = rendered_compose_path()
    if not compose.is_file():
        compose = render_langfuse_compose()
    print(f"→  compose down langfuse-stack (project={project_name()})")
    duk.compose_down(
        project_dir=langfuse_dir(),
        compose_file=compose,
        project_name=project_name(),
        volumes=volumes,
    )
    print("OK  stopped langfuse-stack")


def langfuse_ui_healthy() -> tuple[bool, str]:
    port = langfuse_ui_port()
    last = f"Langfuse UI :{port} unreachable"
    for host in (bind_host(), "127.0.0.1"):
        url = f"http://{host}:{port}/"
        try:
            code, _ = duk.http_get(url, timeout=5.0)
            if code < 500:
                return True, f"Langfuse UI {url} → HTTP {code}"
            last = f"Langfuse UI {url} → HTTP {code}"
        except duk.DockerError as exc:
            last = str(exc)
    return False, last


def wait_langfuse_healthy(timeout_s: int = 300) -> None:
    deadline = time.time() + timeout_s
    last = "not checked"
    while time.time() < deadline:
        try:
            ok, last = langfuse_ui_healthy()
        except Exception as exc:  # noqa: BLE001 — UI may reset during ClickHouse boot
            ok = False
            last = f"probe error: {exc}"
        if ok:
            print(f"OK  {last}")
            return
        time.sleep(4)
    raise RuntimeError(f"timeout waiting for Langfuse UI: {last}")


def check_collector_langfuse_link() -> list[str]:
    """B15: collector config + auth env point at Langfuse OTLP ingest."""
    notes: list[str] = []
    otel_dir = resolve_sibling("OTEL_STACK_PATH", "../otel-collector-stack")
    cfg = otel_dir / "otel-collector-config.yaml"
    if not cfg.is_file():
        raise RuntimeError(f"missing collector config: {cfg}")
    text = cfg.read_text(encoding="utf-8")
    if "otlphttp/langfuse" not in text and "langfuse" not in text.lower():
        raise RuntimeError("collector config has no Langfuse exporter (expected otlphttp/langfuse)")
    if "langfuse-web:3000" not in text and "langfuse" not in text:
        notes.append("WARN collector endpoint may not target langfuse-web:3000")
    else:
        notes.append("collector config references Langfuse OTLP ingest")

    otel_env = otel_dir / ".env"
    auth = env("AUTHORIZATION", "")
    if otel_env.is_file():
        for raw in otel_env.read_text(encoding="utf-8").splitlines():
            if raw.startswith("AUTHORIZATION="):
                auth = auth or raw.split("=", 1)[1].strip()
    if not auth:
        raise RuntimeError(
            "AUTHORIZATION empty in otel-collector-stack/.env — "
            "collector→Langfuse Basic auth required for ingest"
        )
    notes.append("AUTHORIZATION present for collector→Langfuse")

    # Same docker network?
    res = duk.run(
        ["docker", "network", "inspect", env("PROXY_NETWORK_NAME", "proxy_network") or "proxy_network"],
        timeout=30,
    )
    if res.ok and "langfuse-web" in res.stdout and "otel-collector" in res.stdout:
        notes.append("proxy_network contains langfuse-web and otel-collector")
    elif res.ok:
        notes.append(
            "WARN proxy_network inspect did not list both service names yet "
            "(ok if containers use different name prefixes)"
        )
    return notes


def langfuse_image_audit() -> tuple[bool, str]:
    """B20 audit on rendered langfuse compose after P2-1 pins.

    Untagged / :latest / major-only tags (:3, :7) are hard failures.
    Digest pins (@sha256:…) are accepted.
    """
    path = rendered_compose_path()
    if not path.is_file():
        path = render_langfuse_compose()
    images = images_from_compose_text(path.read_text(encoding="utf-8"))
    bad = assert_no_latest(images)
    floating = _floating_major_tags(images)
    if bad or floating:
        return False, f"unpinned images after render: latest/untagged={bad} major-only={floating}"
    return True, f"langfuse images ok ({len(images)} refs); pins applied (P2-1)"


def assert_langfuse_down_fails_smoke() -> str:
    """B18 subset: wrong UI port must fail clearly."""
    bad_port = langfuse_ui_port() + 333
    url = f"http://127.0.0.1:{bad_port}/"
    opener = request.build_opener(request.ProxyHandler({}))
    try:
        opener.open(request.Request(url), timeout=2)
        raise RuntimeError(f"expected failure probing {url} but request succeeded")
    except error.URLError as exc:
        return f"intentional bad endpoint {url} failed as expected: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"intentional bad endpoint {url} failed as expected: {exc}"
