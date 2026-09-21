# Ecom thin adapter (P2-2)

Wire the existing sibling **`ecom-workflow`** to OBS Quality Kit L2/L3. **Do not relocate the repo; do not rebuild a mini-ecom.**

中文版：[../zh/ECOM_ADAPTER.md](../zh/ECOM_ADAPTER.md)

---

## Boundary (Review P2-2)

| Allowed | Forbidden |
|---------|-----------|
| `.env` / compose `OBS_QUALITY_GATE_MODE` | Moving business / LLM / pricing logic into the kit |
| `/health` exposing gate + Scheme B fields | Forking a second golden path inside ecom |
| Cross-links + kit B smoke | God-workflow / large Code copies of the contract in n8n |
| Reuse ecom’s primary trust path | Defaulting the gate to `block` |

Gate default is **`shadow`**: record only; does not block writes.

---

## Ecom-side patch list

Relative to `ECOM_WORKFLOW_PATH` (default `../ecom-workflow`):

1. `.env.example` / `.env`: `OBS_QUALITY_GATE_MODE=shadow`
2. `docker/compose.yml`: inject that env into `ecom_python_ai`
3. `python-service/quality_gate.py`: parse shadow|block
4. `GET /health`: return  
   `obs_quality_gate_mode`, `obs_quality_gate_blocks_writes`, `correlation_id`, `trace_id`
5. `docs/*/OBSERVABILITY.md`: link back here

Business pipelines stay owned by **ecom-workflow**. When no sibling `smoke_*_primary.py` exists, kit B asserts the OBS subset only (health / gate / Jaeger).

---

## How to run

```bash
# 1) Base stack (kit)
cd ../obs-quality-kit && ./scripts/bootstrap.sh up --profile base

# 2) Ecom sidecar (if not already up)
cd ../ecom-workflow
docker compose -f docker/compose.yml --env-file .env up -d --build

# 3) Kit layer B (static + live when reachable)
cd ../obs-quality-kit
python3 scripts/smoke_kit_ecom_path.py
```

| Check | Coverage |
|-------|----------|
| E1 | `GET /health` (incl. DB) |
| E5 | Response includes correlation + trace |
| E6 | Jaeger search by **`trace_id`** (not correlation UUID) |
| E7 | Soft-check when `/health.langfuse=configured`; else skip |
| E8 | Fake `trace_id` → not in Jaeger |
| E9 | `obs_quality_gate_mode=shadow` and `obs_quality_gate_blocks_writes=false` |

---

## Review checklist

- [x] No large logic fork into the kit / four repos
- [x] Gate remains shadow by default
- [x] Docs state the repo stays independent
