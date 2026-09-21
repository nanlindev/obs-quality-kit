"""Quality gate mode (L2) — independent of n8n / Sheets / ERP adapters."""

from __future__ import annotations

from enum import Enum


class GateMode(str, Enum):
    """Outbound / write gate for quality signals.

    shadow — default: record scores/trails; do NOT block business writes
    block  — explicit: adapters MAY refuse writes when quality fails
    """

    SHADOW = "shadow"
    BLOCK = "block"


DEFAULT_GATE_MODE = GateMode.SHADOW

_ALIASES = {
    "shadow": GateMode.SHADOW,
    "observe": GateMode.SHADOW,
    "soft": GateMode.SHADOW,
    "block": GateMode.BLOCK,
    "hard": GateMode.BLOCK,
    "enforce": GateMode.BLOCK,
}


def parse_gate_mode(value: str | None, *, default: GateMode = DEFAULT_GATE_MODE) -> GateMode:
    if value is None or not str(value).strip():
        return default
    key = str(value).strip().lower()
    if key not in _ALIASES:
        raise ValueError(f"invalid gate mode {value!r}; expected shadow|block")
    return _ALIASES[key]


def should_block_writes(mode: GateMode | str | None) -> bool:
    """True only when gate is explicitly block (Review-4: default is never block)."""
    parsed = mode if isinstance(mode, GateMode) else parse_gate_mode(mode)
    return parsed is GateMode.BLOCK
