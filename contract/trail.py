"""Processing trail query convention (aligned with doc-workflow /ops/trail)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class TrailQuery:
    """Language-agnostic trail lookup keys."""

    correlation_id: str | None = None
    trace_id: str | None = None
    limit: int = 200

    def validate(self) -> None:
        if not (self.correlation_id or self.trace_id):
            raise ValueError("correlation_id_or_trace_id_required")
        if self.limit < 1 or self.limit > 1000:
            raise ValueError("limit must be 1..1000")


def trail_query_url(
    base_url: str,
    query: TrailQuery,
    *,
    path: str = "/ops/trail",
) -> str:
    """Build GET URL for a trail endpoint (doc default: /ops/trail).

    Adapters may expose an equivalent path; field names stay the same.
    """
    query.validate()
    base = base_url.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    params: dict[str, str | int] = {"limit": query.limit}
    if query.correlation_id:
        params["correlation_id"] = query.correlation_id
    if query.trace_id:
        params["trace_id"] = query.trace_id
    return f"{base}{path}?{urlencode(params)}"


# Expected JSON shape (informative; adapters may add fields):
# {
#   "correlation_id": "<uuid>",
#   "trace_id": "<32-hex>|null",
#   "events": [ { "stage": "...", "status": "...", "at": "..." }, ... ]
# }
TRAIL_RESPONSE_HINT = (
    "Trail responses SHOULD include correlation_id, optional trace_id, "
    "and an ordered events[] list. Exact event schema is adapter-defined."
)
