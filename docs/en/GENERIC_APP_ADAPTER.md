# Generic app adapter guide (P2-6)

How to attach a **non-n8n / non-kit vertical** app to OBS Quality Kit L0–L2.  
Covers **Frappe**, **WordPress**, and **generic HTTP/worker** services.

中文版：[../zh/GENERIC_APP_ADAPTER.md](../zh/GENERIC_APP_ADAPTER.md)

---

## Honest boundary (read first)

| This page delivers | **Not** delivered (MVP / this P2) |
|--------------------|-----------------------------------|
| Checklist + effort bands | Frappe / WP / ERP **product** plugins or marketplace packs |
| Same thin-patch mindset as [DOC_ADAPTER](DOC_ADAPTER.md) | Rewriting customer business rules or full ERP integration |
| **Example** [`examples/wp-sme`](../../examples/wp-sme/) (local SME WP) | Treating the example as a turnkey SaaS plugin |
| Marketing-safe “attachable (pilot verified)” | Claiming every remote Woo/WP stack is already tested |

Shipping production adapters = **paid custom / deep delivery** (see [BASE_ADDONS](BASE_ADDONS.md) wire-in Addon).  
Reference verticals remain sibling `doc` / `ecom` / `crm` thin adapters — not a universal SDK.

---

## Capability matrix (PRD §18.2)

| Capability | Attachable to your app? | Notes |
|------------|-------------------------|-------|
| L0 network / safe bind | Yes | Stack-agnostic; UI loopback + reverse proxy |
| L1 OTEL → Jaeger | Yes | App emits OTLP, or sidecar / agent |
| L1 Grafana + Prometheus | Yes | Scrape exporters / cAdvisor; business-agnostic |
| L1 Loki (optional) | Yes | Logs → Loki; see [LOKI](LOKI.md) |
| L1 Langfuse | Only if LLM | Install ≠ wire-in; see [LLM_OPS](LLM_OPS.md) |
| L2 quality contract | Yes | Needs your thin adapter (middleware / hook / worker) |
| L3 n8n facade | **Optional** | Skip for non-n8n apps |

**Do not** change `contract/` Scheme B / default `shadow` semantics to onboard a new app.

---

## Shared thin-adapter checklist (doc-aligned)

Same minimum set for Frappe / WP / custom services:

1. **Process can reach OTLP** → kit `otel-collector:4318` (same `proxy_network` or routable URL)
2. Stable **`OTEL_SERVICE_NAME`** (searchable in Jaeger)
3. Propagate **`X-Correlation-Id`** + optional **`traceparent`**
4. Expose **`correlation_id`** + **`trace_id`** (32 hex; Jaeger uses only the latter)
5. Health (or equivalent) returns  
   `obs_quality_gate_mode`, `obs_quality_gate_blocks_writes` (default **shadow**)
6. If LLM: generation / optional score; metadata includes `correlation_id` ([LLM_OPS](LLM_OPS.md))
7. **Do not** default to `block`; record-only unless the customer explicitly requires hard gates

References: [DOC_ADAPTER](DOC_ADAPTER.md) · [CONTRACT](CONTRACT.md).

---

## Frappe

| Step | Guide-level approach | Rough effort |
|------|----------------------|--------------|
| OTEL | OTLP env on bench / Docker service; or collector agent beside the stack | 0.5–1.5d |
| IDs | API / whitelisted hook injects `correlation_id`; background jobs log or store it | 1–2d |
| Health / gate | Custom whitelisted method or health page exposes shadow fields | 0.5–1d |
| G+P | Run kit `metrics` only; optional process exporter | 0.5d |
| Langfuse | Only if the site calls an LLM; SDK at call sites | 1–3d (wire-in) |
| n8n facade | Usually skip | — |

**Not shipped:** Frappe app, hooks patch pack, one-click bench scripts.

---

## WordPress

| Step | Guide-level approach | Rough effort |
|------|----------------------|--------------|
| OTEL | Native PHP OTLP is awkward → often **sidecar** (access logs → Promtail/Loki, or small proxy) | 1–2d |
| IDs | Plugin / mu-plugin: mint UUID on REST entry; set response headers | 0.5–1.5d |
| Contract fields | Custom REST `GET /obs-health` with gate + IDs | 0.5–1d |
| G+P | Kit metrics; host/container metrics are enough | 0.5d |
| Langfuse | Only when Woo / AI plugins call models | 1–3d |
| n8n facade | Optional WP webhook → n8n; not required | Extra |

**Not shipped (product):** marketplace WP plugin, Woo/LMS one-click stack, PHP OTLP SDK.

### WP SME pilot (shipped example)

In-kit [`examples/wp-sme/`](../../examples/wp-sme/): local **SME marketing site** (official WordPress image; no n8n / no Woo).

| Verified | Still custom |
|----------|--------------|
| `proxy_network` + loopback `:8087` | Elementor / Woo / membership LMS |
| `GET /obs-health/` → `shadow` + `correlation_id` | PHP → Jaeger `trace_id` |
| Docker logs → kit Promtail → Loki (`up --profile loki`) | Hardened remote production WP |

```bash
./scripts/bootstrap.sh up --profile loki
cd examples/wp-sme && docker compose -f compose.yml up -d && ./install.sh
python3 scripts/smoke_kit_wp_sme.py
```

---

## Generic HTTP / worker service

| Step | Guide-level approach | Rough effort |
|------|----------------------|--------------|
| OTEL | `opentelemetry-instrument` / official SDK → Collector | 0.5–1d |
| Contract | Middleware for Scheme B headers; `/health` gate fields | 0.5–1d |
| Golden-path smoke | One happy path + kit-side static checklist (see ecom/crm smokes) | 0.5–1d |
| Langfuse | Only if LLM; install via kit profile | Per [LLM_OPS](LLM_OPS.md) |

Closest ready samples: this monorepo’s `doc` / `ecom` / `crm` Python sidecars.

---

## How to use the effort bands

- Bands assume **one engineer** fluent in Docker + the target stack, including integration buffer; **excluding** business-rule rewrites.  
- Kit **install** (base/metrics/langfuse) and app **wire-in** are separate line items ([BASE_ADDONS](BASE_ADDONS.md)).  
- Demo-ready golden path + green smoke + handbook: add ~1–3d per vertical (doc-adapter class).  
- Beyond the checklist (multi-tenant, ERP document mapping, full eval platforms) → separate quote; out of this guide.

---

## Suggested customer self-check

- [ ] Jaeger finds app spans by **`trace_id`**
- [ ] Same request’s `correlation_id` appears in logs / business store / (if any) Langfuse metadata
- [ ] Health shows `obs_quality_gate_mode=shadow` and writes are not blocked
- [ ] OBS UIs are not public without auth ([SECURITY](SECURITY.md) / [REVERSE_PROXY](REVERSE_PROXY.md))

The kit will **not** auto-generate Frappe/WP repos from this guide.

---

## Review-P2-6

- [x] Guide-first; product WP plugin **not** shipped  
- [x] Paid custom / not-shipped stated  
- [x] Reader can self-estimate effort from tables  
- [x] Shadow default; contract semantics unchanged  
- [x] Optional: local WP SME pilot under `examples/wp-sme/` (logs + `/obs-health`)
