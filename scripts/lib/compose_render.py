"""Rewrite sibling compose publish bindings to OBS_UI_BIND (stdlib, no PyYAML)."""

from __future__ import annotations

import re
from pathlib import Path

# Match common compose port forms:
# - "16686:16686"
# - "4317:4317"
# - "127.0.0.1:16686:16686"
# - '0.0.0.0:4318:4318'
_PORT_LINE = re.compile(
    r"""^(\s*-\s*)['"]?"""
    r"(?:(?P<host>\d+\.\d+\.\d+\.\d+|\[::\]|::|localhost):)?"
    r"(?P<pub>\d+):(?P<tgt>\d+)"
    r"""(?:/(?P<proto>tcp|udp))?['"]?\s*(?:#.*)?$"""
)


def rewrite_publish_bind(compose_text: str, bind_host: str) -> str:
    """Force host publish to bind_host for host:container port mappings."""
    out: list[str] = []
    for line in compose_text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        newline = "\n" if line.endswith("\n") else ""
        match = _PORT_LINE.match(stripped)
        if not match:
            out.append(line)
            continue
        pub = match.group("pub")
        tgt = match.group("tgt")
        proto = match.group("proto")
        suffix = f"/{proto}" if proto else ""
        indent = match.group(1)
        out.append(f'{indent}"{bind_host}:{pub}:{tgt}{suffix}"{newline}')
    return "".join(out)


def render_sibling_compose(
    sibling_compose: Path,
    dest: Path,
    *,
    bind_host: str,
) -> Path:
    text = sibling_compose.read_text(encoding="utf-8")
    rendered = rewrite_publish_bind(text, bind_host)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")
    return dest


def images_from_compose_text(text: str) -> list[str]:
    return re.findall(r"^\s*image:\s*(\S+)\s*$", text, flags=re.MULTILINE)


def assert_no_latest(images: list[str]) -> list[str]:
    """Return list of offending image refs that use :latest or untagged."""
    bad: list[str] = []
    for image in images:
        # digest pins are OK
        if "@sha256:" in image:
            continue
        if image.endswith(":latest") or ":" not in image.split("/")[-1]:
            bad.append(image)
    return bad
