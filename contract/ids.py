"""Scheme B ID helpers: correlation_id + trace_id + traceparent (stdlib only)."""

from __future__ import annotations

import re
import secrets
import uuid
from dataclasses import dataclass
from typing import Mapping

_CORR_HEADER = ("x-correlation-id", "correlation-id")
_TRACEPARENT_RE = re.compile(
    r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$",
    re.IGNORECASE,
)
_TRACE_ID_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)


def is_valid_correlation_id(value: str | None) -> bool:
    if not value:
        return False
    try:
        uuid.UUID(str(value).strip())
        return True
    except ValueError:
        return False


def ensure_correlation_id(value: str | None = None) -> str:
    """Return a canonical UUID string; generate when missing/invalid."""
    if value and is_valid_correlation_id(value):
        return str(uuid.UUID(str(value).strip()))
    return str(uuid.uuid4())


def is_valid_trace_id(value: str | None) -> bool:
    if not value:
        return False
    return bool(_TRACE_ID_RE.match(value.strip())) and value.strip().lower() != "0" * 32


def generate_trace_id() -> str:
    """Generate a random 32-hex OTEL/W3C trace_id (for examples / offline demos)."""
    while True:
        tid = secrets.token_hex(16)
        if tid != "0" * 32:
            return tid


def generate_span_id() -> str:
    while True:
        sid = secrets.token_hex(8)
        if sid != "0" * 16:
            return sid


def build_traceparent(
    *,
    trace_id: str | None = None,
    parent_span_id: str | None = None,
    sampled: bool = True,
) -> str:
    """Build W3C traceparent: 00-{trace_id}-{span_id}-{flags}."""
    tid = (trace_id or generate_trace_id()).lower()
    if not is_valid_trace_id(tid):
        raise ValueError(f"invalid trace_id: {trace_id!r}")
    sid = (parent_span_id or generate_span_id()).lower()
    if len(sid) != 16 or not re.fullmatch(r"[0-9a-f]{16}", sid):
        raise ValueError(f"invalid parent_span_id: {parent_span_id!r}")
    flags = "01" if sampled else "00"
    return f"00-{tid}-{sid}-{flags}"


def parse_traceparent(value: str | None) -> dict[str, str] | None:
    if not value:
        return None
    match = _TRACEPARENT_RE.match(value.strip())
    if not match:
        return None
    tid, sid, flags = match.group(1).lower(), match.group(2).lower(), match.group(3).lower()
    if tid == "0" * 32 or sid == "0" * 16:
        return None
    return {"trace_id": tid, "parent_span_id": sid, "flags": flags}


def is_valid_traceparent(value: str | None) -> bool:
    return parse_traceparent(value) is not None


def correlation_id_from_headers(headers: Mapping[str, str]) -> str | None:
    carrier = {k.lower(): v for k, v in headers.items()}
    for key in _CORR_HEADER:
        raw = (carrier.get(key) or "").strip()
        if raw:
            return raw
    return None


def traceparent_from_headers(headers: Mapping[str, str]) -> str | None:
    carrier = {k.lower(): v for k, v in headers.items()}
    raw = (carrier.get("traceparent") or "").strip()
    return raw or None


@dataclass(frozen=True)
class RequestIds:
    """Resolved Scheme B IDs for one request/context."""

    correlation_id: str
    trace_id: str
    traceparent: str

    def as_dict(self) -> dict[str, str]:
        return {
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "traceparent": self.traceparent,
        }

    def response_headers(self) -> dict[str, str]:
        return {
            "X-Correlation-Id": self.correlation_id,
            "X-Trace-Id": self.trace_id,
            "traceparent": self.traceparent,
        }


def resolve_ids(
    *,
    body_correlation_id: str | None = None,
    headers: Mapping[str, str] | None = None,
    trace_id: str | None = None,
    generate_trace_if_missing: bool = True,
) -> RequestIds:
    """Prefer body → header correlation_id; derive/generate trace_id + traceparent."""
    headers = headers or {}
    header_corr = correlation_id_from_headers(headers)
    correlation_id = ensure_correlation_id(body_correlation_id or header_corr)

    tp = parse_traceparent(traceparent_from_headers(headers))
    tid = (trace_id or (tp["trace_id"] if tp else None) or "").strip().lower()
    if tid and not is_valid_trace_id(tid):
        tid = ""
    if not tid:
        if not generate_trace_if_missing:
            raise ValueError("trace_id missing and generate_trace_if_missing=False")
        tid = generate_trace_id()

    parent = tp["parent_span_id"] if tp else None
    traceparent = build_traceparent(trace_id=tid, parent_span_id=parent)
    return RequestIds(
        correlation_id=correlation_id,
        trace_id=tid,
        traceparent=traceparent,
    )
