# Quality contract (L2)

Language-agnostic field table. **Source of truth = this doc + the `contract/` package.**  
n8n node / workflow names are **not** the contract; any HTTP/worker/sidecar may implement it.

中文版：[../zh/CONTRACT.md](../zh/CONTRACT.md)

---

## 1. Scheme B identifiers

| Field | Shape | Use |
|-------|-------|-----|
| `correlation_id` | UUID string | Business audit, trail, cards; allocate or pass through at entry |
| `trace_id` | 32-char lowercase hex (OTEL/W3C) | **Paste into Jaeger only**; never treat a UUID as the Jaeger key |
| `traceparent` | `00-{trace_id}-{span_id}-{flags}` | Propagate downstream; span attributes SHOULD include `correlation_id` |

### HTTP conventions (adapters may mirror)

| Direction | Convention |
|-----------|------------|
| Request headers | `X-Correlation-Id` (or `correlation-id`); optional `traceparent` |
| Request body | optional `correlation_id` (preferred over header) |
| Response headers | `X-Correlation-Id`, `X-Trace-Id`, prefer echoing `traceparent` |
| Response body | at least `correlation_id`; `trace_id` when a span is active |

### Example shape (library-generated; no n8n)

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}
```

```bash
python3 scripts/contract_example.py
```

---

## 2. Gate mode (Review-4)

| Mode | Meaning |
|------|---------|
| **`shadow` (default)** | Record scores/trails/signals; do **not** block business writes on quality failure |
| **`block`** | Explicit opt-in; adapters **may** refuse writes (Sheets/ERP/etc.) |

test vs production semantics stay adapter-defined (e.g. skip Sheets in test). **Default gate must not be block.**

Suggested env (optional): `OBS_QUALITY_GATE_MODE=shadow|block`

---

## 3. Processing trail

Queryable by `correlation_id` and/or `trace_id`.

doc-workflow reference:

```http
GET {sidecar}/ops/trail?correlation_id={uuid}
GET {sidecar}/ops/trail?trace_id={32hex}&limit=200
```

Kit helper: `contract.trail.trail_query_url`. Responses SHOULD include `correlation_id`, optional `trace_id`, and ordered `events[]` (event schema is vertical-owned).

---

## 4. Langfuse hooks (when LLM exists)

| Capability | Requirement |
|------------|-------------|
| generation | Correlatable via `trace_id` / `correlation_id` |
| score (optional) | Attached to a Langfuse **trace**; **metadata** SHOULD include `correlation_id` (and business keys); consumable by gates; skip entire L when no LLM / no keys |

**Correlation (P2-5):**

- `correlation_id` → business lookup (trail / Sheets / Slack / score metadata)
- `trace_id` → glue for Jaeger **and** Langfuse traces (32 hex; never search Jaeger with the correlation UUID)
- score `name`/`value` owned by the vertical; kit does not force a name list

Sample + install≠wire-in: [LLM_OPS.md](LLM_OPS.md). Deeper Prompt/Dataset: **link** sibling doc `PHASE2_LANGFUSE_ADDENDUM` (not rebuilt here).

Prompt version storage is **not** owned by the kit contract (prefer the vertical repo).

---

## 5. Orchestrator-decoupling checklist (Review-4)

- [ ] Field table does not treat n8n node names as sole truth
- [ ] `contract/` unit tests run without Docker / n8n
- [ ] Default `GateMode.shadow`; `should_block_writes` true only for `block`
- [ ] Trail URL convention is not bound to a workflow name

---

## 6. Non-goals (MVP)

Full dataset eval platforms, multi-tenant control-plane UI, replacing vertical business rules.
