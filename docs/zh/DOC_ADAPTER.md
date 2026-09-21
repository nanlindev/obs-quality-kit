# Doc thin adapter（Stage 6）

在现有 sibling **`doc-workflow`** 上接入 OBS Quality Kit L2/L3，**不搬仓、不重做轻量 doc**。

英文版：[../en/DOC_ADAPTER.md](../en/DOC_ADAPTER.md)

---

## 边界（Review-6）

| 允许 | 禁止 |
|------|------|
| `.env` / compose 传入 `OBS_QUALITY_GATE_MODE` | 把业务规则、LLM、Sheets 逻辑搬进 kit |
| `/health` 暴露闸门与 Scheme B 字段 | 在 doc 里分叉出第二套金路径 |
| 文档互链 + kit 侧 B smoke | god-workflow / 大段 Code 复制契约进 n8n |
| 沿用 doc 主信任路径做金路径 | 默认 `block` 闸门 |

闸门默认 **`shadow`**：只记录，不阻断 Sheets/post（与 doc 自有的 test/production Sheets 闸门无关）。

---

## doc 侧补丁清单

相对 `DOC_WORKFLOW_PATH`（默认 `../doc-workflow`）：

1. `.env.example` / `.env`：`OBS_QUALITY_GATE_MODE=shadow`
2. `docker/compose.yml`：把该 env 注入 `doc_python_ai`
3. `python-service/quality_gate.py`：解析 shadow|block
4. `GET /health`：返回  
   `obs_quality_gate_mode`、`obs_quality_gate_blocks_writes`、`correlation_id`、`trace_id`
5. `docs/*/OBSERVABILITY.md`：链回本文

业务流水线（ingest → extract → validate → review → post）**保持 doc 仓所有权**。

---

## 金路径怎么跑

```bash
# 1) 底座（kit）
cd ../obs-quality-kit && ./scripts/bootstrap.sh up --profile base

# 2) doc sidecar（若尚未起）
cd ../doc-workflow
docker compose -f docker/compose.yml --env-file .env up -d --build

# 3) doc 主路径 smoke（D1–D4 + trail）
python3 scripts/smoke_doc_primary.py

# 4) kit B 层（静态 + 可达则 live：健康/闸门/Jaeger/负例 + 调用上一步）
cd ../obs-quality-kit
python3 scripts/smoke_kit_doc_path.py
```

| PRD §16.3 | 覆盖 |
|-----------|------|
| D1 | `GET /health` |
| D2–D4 | `smoke_doc_primary`（demo / bad+mismatch / duplicate） |
| D5 | 响应与 trail 含 correlation + trace |
| D6 | Jaeger 用 **`trace_id`**（不是 correlation UUID） |
| D7 | `/health.langfuse=configured` 时软检；否则 skip |
| D8 | 伪造 `trace_id` → Jaeger 查不到，失败信息可读 |
| D9 | `obs_quality_gate_mode=shadow` 且 `obs_quality_gate_blocks_writes=false` |
| L10（P2-5） | 薄 LLM Ops：`smoke_kit_llm_ops.py`（score 关联文档 + 有密钥则金路径；无密钥 skip） |

更深 Prompt/Dataset 样板外链：sibling `PHASE2_LANGFUSE_ADDENDUM`（见 [LLM_OPS](LLM_OPS.md)）。

---

## 与 Stage 5 facade 的关系

- Facade = kit 仓薄入口画布（健康探测）
- Doc adapter = **垂直金路径**；facade **不**替代 Doc Process / Post

---

## Review-6 勾选

- [x] 无大段逻辑叉进 kit / 四仓分叉
- [x] 闸门仍 shadow 默认
- [x] 文档写明「仓仍独立」
