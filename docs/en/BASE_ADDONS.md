# Base / Addons ↔ engineering profiles

Maps commerce (Gig) language to compose **engineering profiles**. Related, **not** synonymous.

中文版：[../zh/BASE_ADDONS.md](../zh/BASE_ADDONS.md)

---

## Mapping table

| Commerce (PRD) | Engineering profile / delivery | Out of scope |
|----------------|--------------------------------|--------------|
| **Base** | `base`: O+J, bootstrap, handbooks, smoke A, safe default bind | No customer business code changes; no default G+P / L |
| **Addon: Metrics (G+P)** | `metrics`: kit Grafana+Prom+cAdvisor + [METRICS](METRICS.md) | Full custom business alerting |
| **Addon: Langfuse install** | `langfuse`: L UI + collector wiring + smoke B15 | Full LLM Ops / deep sidecar changes |
| **Addon: Loki (logs)** | `loki`: kit Loki+Promtail + [LOKI](LOKI.md); may co-run with metrics | Full ELK; do not co-run with full long-term |
| **Addon: quality or LLM wire-in (1 flow)** | Contract + MVP=`doc` golden path ([DOC_ADAPTER](DOC_ADAPTER.md)) | Unlimited scope; second flow is extra |
| **Addon: maintenance / upgrade** | Image pin bumps + smoke regression | Automatic `latest` |
| Portfolio “full stack” (not a SKU name) | `full` = metrics + langfuse (**excludes** loki) | Avoid long-term on ≤8GB hosts |

Do **not** hard-map Fiverr “three packages” onto the three profile names `base|metrics|full`.

---

## Install Addon vs wire-in Addon

| Kind | Meaning | One-shot scripts? |
|------|---------|-------------------|
| **Install** | Stack up, UI/ingest OK, smoke green | Yes (bootstrap + smoke) |
| **Wire-in** | Change sidecar prompts / scores / gate behavior | **No** automation; deep delivery |

Thin LLM Ops (score ↔ Scheme B, honest skip): [LLM_OPS.md](LLM_OPS.md).

---

## Extending

New L1 backends: [EXTEND_PROFILE](EXTEND_PROFILE.md). `loki` is registered (P2-4). Unregistered names = upgrade/custom, not a supported profile.
