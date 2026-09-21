# Phase-2 Addendum (OBS Quality Kit)

| | |
|--|--|
| Version | 0.2-p2-smoke-green |
| Parent | [PRD.md](PRD.md) §11 / later Phase-2 sections |
| Plan | `~/.cursor/plans/obs_kit_phase2_ccd847de.plan.md` |
| Prerequisite | [P1_CLOSE.md](P1_CLOSE.md) — A+B smoke green |
| Close | [P2_CLOSE.md](P2_CLOSE.md) — P2-7 regression green |
| Film gate | **Film = P2-8** (P2-0…P2-7 already green; no mid-P2 75s cuts) |

中文版：[../zh/PHASE2_ADDENDUM.md](../zh/PHASE2_ADDENDUM.md)

**This Addendum is incremental.** It does not rewrite the full PRD. Positioning / L0–L3 / Scheme B / shadow default stay.

---

## 1. Relation to P1

| P1 delivered | P2 adds |
|--------------|---------|
| Bootstrap + O+J; profiles `base`/`metrics`/`langfuse`/`full` | Pin P1 WARNs; profile `loki` |
| Contract + facade + **doc** thin adapter | **ecom** / **crm** thin adapters (same pattern) |
| Handbooks + unfilmed shot list | Generic app guide; thin LLM Ops; film after green |
| `smoke_kit_p1.py` | `smoke_kit_p2.py` regression pack |

Pattern remains [DOC_ADAPTER.md](DOC_ADAPTER.md): **no repo relocate**; verticals only env/health/gate/cross-links; kit owns smoke + docs.

---

## 2. In-scope

| Stage | Content | Must be green before film? |
|-------|---------|----------------------------|
| **P2-0** | This doc + PRD links | Yes (docs) |
| **P2-1** | Pin Langfuse/MinIO (clear P1 B20 WARN) | Yes |
| **P2-2** | ecom thin adapter + `smoke_kit_ecom_path.py` | Yes |
| **P2-3** | crm thin adapter + `smoke_kit_crm_path.py` | Yes |
| **P2-4** | Loki profile (standalone; may run with metrics) + smoke | Yes |
| **P2-5** | Thin LLM Ops (score / correlation docs; prefer doc+L) | Yes |
| **P2-6** | `GENERIC_APP_ADAPTER` (Frappe/WP/generic — **no impl code**) | Yes |
| **P2-7** | `smoke_kit_p2.py` + `P2_CLOSE` + shot-list ecom/crm/Loki flash | Yes |
| **P2-8** | Full + short film cuts | Yes (final gate) |

**P2 “fully complete”:** P2-0…P2-7 accepted **and** P2-8 films checked in.

---

## 3. Out of scope (this P2)

- Frappe / WordPress **code implementation** (guide only)
- Tempo / Sentry / K8s / social verticals
- Reworking vertical golden paths or forking bootstrap/G+P into ecom/crm
- Defaulting the quality gate to `block`
- Mid-P2 Fiverr 75s / public film cuts
- Full dataset eval platforms, multi-tenant prompt IDE, Helicone replacement (P2-5 boundary)

---

## 4. Engineering locks

| Topic | Lock |
|-------|------|
| Adapter | Match doc: `OBS_QUALITY_GATE_MODE`, health Scheme B + gate fields, bilingual `*_ADAPTER.md`, kit smoke |
| Loki | **Standalone** profile `loki`; may co-run with `metrics`; **not** folded into default `full` (avoid long-lived full+loki on 8GB) |
| LLM Ops | Keep install Addon vs wire-in Addon distinct; shadow default |
| Images | Follow [IMAGE_PIN.md](IMAGE_PIN.md); P2-1 clears MinIO / floating-major WARNs |
| Film | Beats in [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md); VO must cover `trace_id`, Base+Addon, not cheap turnkey |

---

## 5. Acceptance summary

| Stage | Expect |
|-------|--------|
| P2-0 | This doc lists stages; film=after P2 green; PRD linked |
| P2-1 | `smoke --profile langfuse|full` green; no auditable `latest` (or documented exception) |
| P2-2/3 | Vertical health + Jaeger/`trace_id` + shadow; repo independent |
| P2-4 | At least one queryable log line (or documented probe); no `contract/` semantic change |
| P2-5 | With L keys: score/annotation visible; else skip |
| P2-6 | Reader can estimate effort; honest “no impl” |
| P2-7 | P2 ordered/one-shot green; P1 does not regress |
| P2-8 | Full + short cuts checked in |

Details and Reviews live in the decompose plan; do not advance on a red stage.

---

## 6. Status flow

| Status | Meaning |
|--------|---------|
| `0.2-p2-planning` | Addendum written |
| `0.2-p2-implementing` | From P2-1 onward |
| `0.2-p2-smoke-green` | P2-7 green, pre-film (**current**) |
| `0.2-p2-complete` | Includes P2-8 film |

After P2-7, bump this page and the PRD header to `smoke-green`.
