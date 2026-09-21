# OBS Kit Facade — 导入说明（Stage 5）

薄 n8n 门面：展示 Scheme B ID + 一次健康探测。**不是** doc 金路径，不含业务写出。

英文版：[../en/FACADE_INSTALL.md](../en/FACADE_INSTALL.md)

## 前置

- `platform-n8n` 已运行（共享 n8n）
- 可选：`doc-workflow` sidecar 健康（默认探测 `http://doc_python_ai:8001/health`）
- 或设置 n8n 环境变量 `OBS_FACADE_HEALTH_URL` 指向任意 `/health`

## 导入（platform-n8n）

1. 打开 n8n UI（通常 http://localhost:5678）
2. **Workflows → Import from File**
3. 选择本仓 [`workflows/OBS Kit Facade.json`](../../workflows/OBS%20Kit%20Facade.json)
4. 激活工作流（Webhook 入口需要 Active）

标签建议：`obs-quality-kit`

## 凭证重绑

本 facade **不依赖** Slack / Sheets / DB 凭证。  
若你后来加了第三方节点：导入后在节点上 **Re-bind credentials**；Error Workflow 若引用需手工重绑 ID。

## 怎么跑通最小链

| 方式 | 操作 | 期望 |
|------|------|------|
| Manual | 打开工作流 → **Test workflow** / Execute | 末节点含 `correlation_id`、`trace_id`、`health` |
| Webhook | `POST /webhook/obs-kit-facade`（或 Test URL） | JSON 含 Scheme B 字段 + health |

可选 body：`{"correlation_id":"<uuid>"}` 透传业务 ID。

闸门展示字段 `gate_mode` 默认 **shadow**（不挡写出）。

## Review-5

- 节点少：Trigger → Build IDs → GET Health → Format → Done
- `GET Health` 的 error 口已接到 `Format Health Error`（无悬空）
- 不 Execute Doc Process / Post，避免变成 god-workflow

## 静态检查（无需 n8n）

```bash
python3 scripts/smoke_kit_facade.py
```
