# 质量契约（L2）

语言无关字段表与约定。**真相源 = 本文 + 本仓 `contract/` 包**。  
n8n 节点名、工作流名 **不是**契约；任意 HTTP/worker/sidecar 都可实现。

英文版：[../en/CONTRACT.md](../en/CONTRACT.md)

---

## 1. Scheme B 标识

| 字段 | 形态 | 用途 |
|------|------|------|
| `correlation_id` | UUID 字符串 | 业务审计、trail、Slack/卡片；入口分配或透传 |
| `trace_id` | 32 位小写 hex（OTEL/W3C） | **仅此可粘贴进 Jaeger**；勿把 UUID 当 Jaeger 键 |
| `traceparent` | `00-{trace_id}-{span_id}-{flags}` | 传入下游；span attribute 应带 `correlation_id` |

### HTTP 约定（适配器可等价实现）

| 方向 | 约定 |
|------|------|
| 请求头 | `X-Correlation-Id`（或 `correlation-id`）；可选 `traceparent` |
| 请求体 | 可选 `correlation_id`（优先于头） |
| 响应头 | `X-Correlation-Id`、`X-Trace-Id`、建议回传 `traceparent` |
| 响应体 | 至少含 `correlation_id`；有活跃 span 时含 `trace_id` |

### 示例形状（库生成，不依赖 n8n）

```json
{
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}
```

```bash
python3 scripts/contract_example.py
```

---

## 2. 闸门模式（Review-4）

| 模式 | 含义 |
|------|------|
| **`shadow`（默认）** | 记录分数/trail/告警信号；**不**因质检失败阻断业务写出 |
| **`block`** | 显式开启后，适配器**可以**拒绝写出（Sheets/ERP 等） |

环境（test / production）由适配器解释（例如 test 下跳过 Sheets）；**不得**把默认闸门设成 block。

环境变量建议名（非强制）：`OBS_QUALITY_GATE_MODE=shadow|block`

---

## 3. Processing trail

可按 `correlation_id` 和/或 `trace_id` 查询阶段事件。

doc-workflow 参考实现：

```http
GET {sidecar}/ops/trail?correlation_id={uuid}
GET {sidecar}/ops/trail?trace_id={32hex}&limit=200
```

kit 库：`contract.trail.trail_query_url`。响应宜含 `correlation_id`、可选 `trace_id`、有序 `events[]`（事件 schema 由垂直仓定义）。

---

## 4. Langfuse 钩子（有 LLM 时）

| 能力 | 要求 |
|------|------|
| generation | 可与 `trace_id` / `correlation_id` 关联 |
| score（可选） | 挂在 Langfuse **trace** 上；**metadata** 宜含 `correlation_id`（及业务主键）；闸门可消费；无 LLM / 无密钥可跳过整个 L |

**关联约定（P2-5）：**

- `correlation_id` → 业务检索键（trail / Sheets / Slack / score metadata）
- `trace_id` → Jaeger **与** Langfuse trace 的粘合键（32 hex；勿用 correlation UUID 查 Jaeger）
- score `name`/`value` 由垂直仓定义；kit 不枚举强制名单

样板与安装≠接入说明：[LLM_OPS.md](LLM_OPS.md)。更深 Prompt/Dataset：**外链** sibling doc `PHASE2_LANGFUSE_ADDENDUM`（本契约不重做）。

kit 契约**不**规定 prompt 版本存储位置（优先落在垂直仓）。

---

## 5. 与编排器解耦检查（Review-4）

- [ ] 字段表无「仅某某 n8n 节点」作为唯一真相
- [ ] `contract/` 可在无 Docker / 无 n8n 环境下跑单测
- [ ] 默认 `GateMode.shadow`；`should_block_writes` 仅对 `block` 为真
- [ ] trail URL 约定不绑定具体工作流名

---

## 6. 非目标（MVP）

完整 dataset 评测平台、多租户控制面 UI、替代垂直仓业务规则。
