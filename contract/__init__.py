"""OBS Quality Kit — L2 quality contract (orchestrator-agnostic).

Scheme B IDs + gate mode + trail query conventions.
Truth source = field table in docs/*/CONTRACT.md + this package.
n8n node names are NOT the contract.
"""

from __future__ import annotations

from .gate import DEFAULT_GATE_MODE, GateMode, parse_gate_mode
from .ids import (
    RequestIds,
    build_traceparent,
    ensure_correlation_id,
    generate_trace_id,
    is_valid_correlation_id,
    is_valid_trace_id,
    is_valid_traceparent,
    parse_traceparent,
    resolve_ids,
)
from .trail import TrailQuery, trail_query_url

__all__ = [
    "DEFAULT_GATE_MODE",
    "GateMode",
    "RequestIds",
    "TrailQuery",
    "build_traceparent",
    "ensure_correlation_id",
    "generate_trace_id",
    "is_valid_correlation_id",
    "is_valid_trace_id",
    "is_valid_traceparent",
    "parse_gate_mode",
    "parse_traceparent",
    "resolve_ids",
    "trail_query_url",
]
