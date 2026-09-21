# Doc thin adapter (Stage 6)

Wire the existing sibling **`doc-workflow`** to OBS Quality Kit L2/L3. **Do not relocate the repo; do not rebuild a mini-doc.**

中文版：[../zh/DOC_ADAPTER.md](../zh/DOC_ADAPTER.md)

---

## Boundary (Review-6)

| Allowed | Forbidden |
|---------|-----------|
| `.env` / compose `OBS_QUALITY_GATE_MODE` | Moving business / LLM / Sheets logic into the kit |
| `/health` exposing gate + Scheme B fields | Forking a second golden path inside doc |
| Cross-links + kit B smoke | God-workflow / large Code copies of the contract in n8n |
| Reuse doc’s primary trust path | Defaulting the gate to `block` |

Gate default is **`shadow`**: record only; does not block Sheets/post (separate from doc’s own test/production Sheets gates).

---

## Doc-side patch list

Relative to `DOC_WORKFLOW_PATH` (default `../doc-workflow`):

1. `.env.example` / `.env`: `OBS_QUALITY_GATE_MODE=shadow`
2. `docker/compose.yml`: inject that env into `doc_python_ai`
3. `python-service/quality_gate.py`: parse shadow|block
4. `GET /health`: return  
   `obs_quality_gate_mode`, `obs_quality_gate_blocks_writes`, `correlation_id`, `trace_id`
5. `docs/*/OBSERVABILITY.md`: link back here

The business pipeline (ingest → extract → validate → review → post) **stays owned by doc-workflow**.

---

## How to run the golden path

```bash
# 1) Base stack (kit)
cd ../obs-quality-kit && ./scripts/bootstrap.sh up --profile base

# 2) Doc sidecar (if not already up)
cd ../doc-workflow
docker compose -f docker/compose.yml --env-file .env up -d --build

# 3) Doc primary smoke (D1–D4 + trail)
python3 scripts/smoke_doc_primary.py

# 4) Kit layer B (static + live when reachable)
cd ../obs-quality-kit
python3 scripts/smoke_kit_doc_path.py
```

| PRD §16.3 | Coverage |
|-----------|----------|
| D1 | `GET /health` |
| D2–D4 | `smoke_doc_primary` (demo / bad+mismatch / duplicate) |
| D5 | Response + trail include correlation + trace |
| D6 | Jaeger search by **`trace_id`** (not the correlation UUID) |
| D7 | Soft-check when `/health.langfuse=configured`; else skip |
| D8 | Fake `trace_id` → not in Jaeger; failure message readable |
| D9 | `obs_quality_gate_mode=shadow` and `obs_quality_gate_blocks_writes=false` |
| L10 (P2-5) | Thin LLM Ops: `smoke_kit_llm_ops.py` (score correlation docs + golden path when keys set; skip without keys) |

Deeper Prompt/Dataset sample (external): sibling `PHASE2_LANGFUSE_ADDENDUM` (see [LLM_OPS](LLM_OPS.md)).

---

## Relation to Stage 5 facade

- Facade = thin kit entry canvas (health probe)
- Doc adapter = **vertical golden path**; facade does **not** replace Doc Process / Post

---

## Review-6 checklist

- [x] No large logic fork into the kit / four repos
- [x] Gate remains shadow by default
- [x] Docs state the repo stays independent
