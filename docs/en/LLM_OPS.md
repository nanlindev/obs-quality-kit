# Thin LLM Ops (P2-5)

On top of the **Langfuse install Addon**, demonstrate a **quality signal (score)** tied to Scheme B IDs.  
This stage does **not** rebuild doc-level Prompt Management / Dataset platforms or ecom·crm triples.

中文版：[../zh/LLM_OPS.md](../zh/LLM_OPS.md)

---

## Install Addon vs wire-in Addon

| Kind | Kit delivers | Out of scope here |
|------|--------------|-------------------|
| **Install** (`profile langfuse`) | UI up, collector linkable, B15 smoke | Changing business prompts / auto-scoring logic |
| **Wire-in** (vertical repo) | Conventions + sample link; kit smoke asserts scores when keys exist | Building a full eval platform for the customer |

See [BASE_ADDONS](BASE_ADDONS.md). **Gate default remains shadow** — scores record only; quality failure must not block business writes in MVP.

---

## Score ↔ Scheme B correlation (contract)

| Field | Where | Use |
|-------|-------|-----|
| `correlation_id` | Score **metadata** + business trail | Same business key across Langfuse / Sheets / Slack |
| `trace_id` | Score attached to Langfuse **trace**; same hex on OTEL | Cross-check Jaeger ↔ Langfuse; **not** the correlation UUID |
| score `name` / `value` | Langfuse Scores | Quality signal; gates **may** consume; MVP does not block |

The kit contract does **not** enumerate score names (vertical owns them). Reference (doc):

| Score name | Type | Meaning |
|------------|------|---------|
| `doc.validation_passed` | BOOLEAN | 1=passed / 0=needs_review |
| `doc.validation_status` | CATEGORICAL | passed / needs_review |
| `doc.confidence` | NUMERIC | Extract confidence |
| `doc.error_count` | NUMERIC | Validation error count |

Code / UI: sibling `doc-workflow` → [`docs/en/LANGFUSE.md`](../../../doc-workflow/docs/en/LANGFUSE.md) · [`scores.py`](../../../doc-workflow/python-service/scores.py).

Deeper sample (Prompt / Dataset / Experiment — **not rebuilt here**):  
[`PHASE2_LANGFUSE_ADDENDUM.md`](../../../doc-workflow/docs/en/PHASE2_LANGFUSE_ADDENDUM.md).

---

## How to accept

```bash
# 1) Install-level (optional)
./scripts/bootstrap.sh up --profile langfuse

# 2) Doc sidecar: set LANGFUSE_PUBLIC_KEY + SECRET (wire-in)
# 3) Kit thin asserts
python3 scripts/smoke_kit_llm_ops.py
```

| Case | Expectation |
|------|-------------|
| `/health.langfuse=skipped` (no keys) | **Honest skip** (same as D7; not a failure) |
| `configured` + golden path | Response includes `langfuse_scores` (ok or explainable skip); UI filterable by score / metadata |
| Gate | Still `shadow`; scores do not block Sheets/post |

---

## Non-goals (P2-5)

Full dataset eval platforms, multi-tenant prompt IDE, Helicone replacement, re-implementing the doc triple on ecom/crm.

---

## Review-P2-5

- [x] Install ≠ wire-in stated
- [x] Score ↔ `correlation_id` / `trace_id` stated
- [x] Link to doc deeper sample; not rebuilt here
- [x] Shadow default; no forced business block
