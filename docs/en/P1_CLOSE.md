# P1 close notes (Stage 9)

| | |
|--|--|
| Status | **P1 complete** (MVP-1 = acceptance A + B full smoke green) |
| Date | 2026-09-16 |
| Film | **Not cut**; **film only after Phase-2 is fully accepted** |
| Next | **Phase-2 in progress** — [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md) (P2-0 done; implement from P2-1) |

## Regression

```bash
# Prefer stacks already up (full):
python3 scripts/smoke_kit_p1.py

# Static only (not a full P1 close):
python3 scripts/smoke_kit_p1.py --static-only
```

This close ran: `base` / `metrics` / `langfuse` / `full` + `smoke_kit_doc_path --live` (incl. `smoke_doc_primary`) + contract / facade / docs.

## Known WARNs (at P1 close; after P2-1)

- ~~Floating Langfuse sibling tags / untagged MinIO~~ → **pinned in P2-1** (see [IMAGE_PIN](IMAGE_PIN.md))
- D7 skips when doc `/health.langfuse=skipped` (no PK/SK; see [DEMO_RUNBOOK](DEMO_RUNBOOK.md))
- Avoid long-lived `full` on ≤8GB hosts

## Phase-2 handoff

Formal scope and stage table: [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md).

PRD Phase-2 sections link here. Decompose plan: `obs_kit_phase2_ccd847de.plan.md`.
