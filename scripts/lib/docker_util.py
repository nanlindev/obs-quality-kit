"""Docker / Compose helpers (stdlib subprocess)."""

from __future__ import annotations

import json
import re
import shutil
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class DockerError(RuntimeError):
    pass


@dataclass
class CmdResult:
    code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.code == 0


def run(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = False,
    timeout: int | None = 120,
) -> CmdResult:
    try:
        proc = subprocess.run(
            list(args),
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise DockerError(f"command not found: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise DockerError(f"timeout running: {' '.join(args)}") from exc
    result = CmdResult(proc.returncode, proc.stdout or "", proc.stderr or "")
    if check and not result.ok:
        raise DockerError(
            f"command failed ({result.code}): {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result


def which_docker() -> str:
    path = shutil.which("docker")
    if not path:
        raise DockerError("docker CLI not found on PATH")
    return path


def daemon_ok() -> tuple[bool, str]:
    try:
        which_docker()
    except DockerError as exc:
        return False, str(exc)
    res = run(["docker", "info"], timeout=30)
    if res.ok:
        return True, "docker daemon reachable"
    msg = (res.stderr or res.stdout or "docker info failed").strip().splitlines()
    return False, msg[-1] if msg else "docker daemon not reachable"


def compose_version() -> tuple[str, tuple[int, int, int] | None]:
    res = run(["docker", "compose", "version", "--short"], timeout=30)
    if not res.ok:
        res = run(["docker", "compose", "version"], timeout=30)
    text = (res.stdout or res.stderr or "").strip()
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not match:
        return text or "unknown", None
    ver = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return match.group(0), ver


def network_exists(name: str) -> bool:
    res = run(["docker", "network", "inspect", name], timeout=30)
    return res.ok


def ensure_network(name: str) -> None:
    if network_exists(name):
        return
    run(["docker", "network", "create", "--driver", "bridge", name], check=True, timeout=60)


def port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def host_port_in_use(port: int) -> bool:
    """True if something accepts TCP on IPv4 loopback or all-interfaces for port."""
    if port_open("127.0.0.1", port):
        return True
    # Also try empty / 0.0.0.0 via connecting to a non-loopback if needed — loopback is enough for conflict.
    return False


def list_listening_binds(port: int) -> list[str]:
    """Return host IP binds for a published container port via docker ps."""
    res = run(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}\t{{.Ports}}",
        ],
        timeout=30,
    )
    if not res.ok:
        return []
    found: list[str] = []
    port_token = f":{port}->"
    alt = f":{port}/"
    for line in res.stdout.splitlines():
        if port_token not in line and f"::{port}->" not in line and f"0.0.0.0:{port}" not in line:
            # also match 127.0.0.1:16686->16686/tcp
            if f":{port}->" not in line and not re.search(rf"(^|[\s,])[^:\s]*:{port}->", line):
                continue
        # Extract bind host for this port
        for match in re.finditer(
            rf"(?P<host>\d+\.\d+\.\d+\.\d+|\[::\]|::):(?P<p>{port})->",
            line,
        ):
            found.append(match.group("host"))
        for match in re.finditer(rf"(?P<host>\d+\.\d+\.\d+\.\d+):{port}->{port}", line):
            if match.group("host") not in found:
                found.append(match.group("host"))
        # docker often shows 0.0.0.0:4317->4317/tcp or :::4317->4317/tcp
        if f"0.0.0.0:{port}->" in line and "0.0.0.0" not in found:
            found.append("0.0.0.0")
        if f":::{port}->" in line or f"[::]:{port}->" in line:
            if "::" not in found:
                found.append("::")
        if f"127.0.0.1:{port}->" in line and "127.0.0.1" not in found:
            found.append("127.0.0.1")
    return found


def container_running_substring(substr: str) -> list[str]:
    res = run(["docker", "ps", "--format", "{{.Names}}"], timeout=30)
    if not res.ok:
        return []
    return [n for n in res.stdout.splitlines() if substr in n]


def compose_up(
    *,
    project_dir: Path,
    compose_file: Path,
    project_name: str,
) -> None:
    run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(project_dir),
            "-f",
            str(compose_file),
            "-p",
            project_name,
            "up",
            "-d",
            "--remove-orphans",
        ],
        check=True,
        timeout=600,
    )


def compose_down(
    *,
    project_dir: Path,
    compose_file: Path,
    project_name: str,
    volumes: bool = False,
) -> None:
    args = [
        "docker",
        "compose",
        "--project-directory",
        str(project_dir),
        "-f",
        str(compose_file),
        "-p",
        project_name,
        "down",
        "--remove-orphans",
    ]
    if volumes:
        args.append("-v")
    run(args, check=True, timeout=300)


def compose_config_images(compose_file: Path, project_dir: Path) -> list[str]:
    res = run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(project_dir),
            "-f",
            str(compose_file),
            "config",
            "--images",
        ],
        timeout=60,
    )
    if not res.ok:
        # fallback: scrape image: lines from file
        text = compose_file.read_text(encoding="utf-8")
        return re.findall(r"image:\s*(\S+)", text)
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    from urllib import error, request
    import http.client
    import socket

    opener = request.build_opener(request.ProxyHandler({}))
    req = request.Request(url, method="GET", headers={"Accept": "application/json,*/*"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read().decode(errors="replace")
    except error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        return exc.code, body
    except (
        error.URLError,
        http.client.RemoteDisconnected,
        ConnectionResetError,
        TimeoutError,
        socket.timeout,
    ) as exc:
        raise DockerError(f"HTTP GET failed {url}: {exc}") from exc


def disk_free_gib(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024**3)


def host_mem_gib() -> float | None:
    """Best-effort total RAM in GiB (macOS/Linux)."""
    import platform
    import sys

    try:
        if platform.system() == "Darwin":
            res = run(["sysctl", "-n", "hw.memsize"], timeout=5)
            if res.ok and res.stdout.strip().isdigit():
                return int(res.stdout.strip()) / (1024**3)
        if sys.platform.startswith("linux"):
            text = Path("/proc/meminfo").read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return kb / (1024**2)
    except Exception:  # noqa: BLE001
        return None
    return None


def parse_json(text: str) -> object:
    return json.loads(text)
