# CRM thin adapter (P2-3)

Wire the existing sibling **`crm-workflow`** to OBS Quality Kit L2/L3. **Do not relocate the repo; do not rebuild a mini-crm.**

中文版：[../zh/CRM_ADAPTER.md](../zh/CRM_ADAPTER.md)

---

## Boundary (Review P2-3)

| Allowed | Forbidden |
|---------|-----------|
| `.env` / compose `OBS_QUALITY_GATE_MODE` | Moving lead / LLM / Sheets logic into the kit |
| `/health` exposing gate + Scheme B fields | Forking a second golden path inside crm |
| Cross-links + kit B smoke | God-workflow / large Code copies of the contract in n8n |
| Reuse crm’s primary trust path | Defaulting the gate to `block` |

Gate default is **`shadow`**: record only; does not block writes.

---

## CRM-side patch list

Relative to `CRM_WORKFLOW_PATH` (default `../crm-workflow`):

1. `.env.example` / `.env`: `OBS_QUALITY_GATE_MODE=shadow`
2. `docker/compose.yml`: inject that env into `crm_python_ai`
3. `python-service/quality_gate.py`: parse shadow|block
4. `GET /health`: return  
   `obs_quality_gate_mode`, `obs_quality_gate_blocks_writes`, `correlation_id`, `trace_id`
5. `docs/*/OBSERVABILITY.md`: link back here

Business pipelines stay owned by **crm-workflow**. When no sibling `smoke_*_primary.py` exists, kit B asserts the OBS subset only (health / gate / Jaeger).

---

## How to run

```bash
# 1) Base stack (kit)
cd ../obs-quality-kit && ./scripts/bootstrap.sh up --profile base

# 2) CRM sidecar (if not already up; needs DEEPSEEK_API_KEY)
cd ../crm-workflow
docker compose -f docker/compose.yml --env-file .env up -d --build

# 3) Kit layer B (static + live when reachable)
cd ../obs-quality-kit
python3 scripts/smoke_kit_crm_path.py
```

| Check | Coverage |
|-------|----------|
| C1 | `GET /health` |
| C5 | Response includes correlation + trace |
| C6 | Jaeger search by **`trace_id`** (not correlation UUID) |
| C7 | Soft-check when `/health.langfuse=configured`; else skip |
| C8 | Fake `trace_id` → not in Jaeger |
| C9 | `obs_quality_gate_mode=shadow` and `obs_quality_gate_blocks_writes=false` |

---

## Review checklist

- [x] No large logic fork into the kit / four repos
- [x] Gate remains shadow by default
- [x] Docs state the repo stays independent
