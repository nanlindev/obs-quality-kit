# CRM thin adapter（P2-3）

在现有 sibling **`crm-workflow`** 上接入 OBS Quality Kit L2/L3，**不搬仓、不重做轻量 crm**。

英文版：[../en/CRM_ADAPTER.md](../en/CRM_ADAPTER.md)

---

## 边界（Review P2-3）

| 允许 | 禁止 |
|------|------|
| `.env` / compose 传入 `OBS_QUALITY_GATE_MODE` | 把线索/LLM/Sheets 逻辑搬进 kit |
| `/health` 暴露闸门与 Scheme B 字段 | 在 crm 里分叉出第二套金路径 |
| 文档互链 + kit 侧 B smoke | god-workflow / 大段 Code 复制契约进 n8n |
| 沿用 crm 主信任路径 | 默认 `block` 闸门 |

闸门默认 **`shadow`**：只记录，不阻断写路径。

---

## crm 侧补丁清单

相对 `CRM_WORKFLOW_PATH`（默认 `../crm-workflow`）：

1. `.env.example` / `.env`：`OBS_QUALITY_GATE_MODE=shadow`
2. `docker/compose.yml`：把该 env 注入 `crm_python_ai`
3. `python-service/quality_gate.py`：解析 shadow|block
4. `GET /health`：返回  
   `obs_quality_gate_mode`、`obs_quality_gate_blocks_writes`、`correlation_id`、`trace_id`
5. `docs/*/OBSERVABILITY.md`：链回本文

业务流水线（enrich / score / memo / outbound 等）**保持 crm 仓所有权**。本仓无独立 `smoke_*_primary.py` 时，kit B 层只断言 OBS 子集（health / gate / Jaeger）。

---

## 怎么跑

```bash
# 1) 底座（kit）
cd ../obs-quality-kit && ./scripts/bootstrap.sh up --profile base

# 2) crm sidecar（若尚未起；需 DEEPSEEK_API_KEY）
cd ../crm-workflow
docker compose -f docker/compose.yml --env-file .env up -d --build

# 3) kit B 层（静态 + 可达则 live）
cd ../obs-quality-kit
python3 scripts/smoke_kit_crm_path.py
```

| 覆盖 | 说明 |
|------|------|
| C1 | `GET /health` |
| C5 | 响应含 correlation + trace |
| C6 | Jaeger 用 **`trace_id`**（不是 correlation UUID） |
| C7 | `/health.langfuse=configured` 时软检；否则 skip |
| C8 | 伪造 `trace_id` → Jaeger 查不到 |
| C9 | `obs_quality_gate_mode=shadow` 且 `obs_quality_gate_blocks_writes=false` |

---

## Review 勾选

- [x] 无大段逻辑叉进 kit / 四仓分叉
- [x] 闸门仍 shadow 默认
- [x] 文档写明「仓仍独立」
