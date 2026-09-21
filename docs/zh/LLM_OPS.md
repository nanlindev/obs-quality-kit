# 薄 LLM Ops（P2-5）

在已有 **Langfuse 安装 Addon** 之上，演示 **质量信号（score）** 与 Scheme B ID 的关联。  
**不**在本 Stage 重做 doc 级 Prompt Management / Dataset 平台 / ecom·crm 三件套。

英文版：[../en/LLM_OPS.md](../en/LLM_OPS.md)

---

## 安装 Addon vs 接入 Addon

| 类型 | 本 kit 交付 | 不交付 |
|------|-------------|--------|
| **安装**（`profile langfuse`） | UI 起来、collector 可接、B15 smoke | 改业务 prompt / 自动打分逻辑 |
| **接入**（垂直仓） | 文档约定 + 样板外链；kit smoke 在配密钥时断言 score | 替客户写完整评测平台 |

详见 [BASE_ADDONS](BASE_ADDONS.md)。**默认闸门仍是 shadow** — score 只记录，不因质量失败阻断业务写路径。

---

## Score ↔ Scheme B 关联（契约）

| 字段 | 放哪里 | 用途 |
|------|--------|------|
| `correlation_id` | score **metadata** + 业务 trail | 在 Langfuse / Sheets / Slack 用同一业务键检索 |
| `trace_id` | score 挂在 Langfuse **trace** 上；OTEL 侧同 hex | Jaeger / Langfuse 互查；**不是** correlation UUID |
| score `name` / `value` | Langfuse Scores | 质量信号；闸门**可**消费，MVP 默认不 block |

kit 契约不规定 score 名枚举（垂直仓自定）。参考实现（doc）：

| Score name | 类型 | 含义 |
|------------|------|------|
| `doc.validation_passed` | BOOLEAN | 1=passed / 0=needs_review |
| `doc.validation_status` | CATEGORICAL | passed / needs_review |
| `doc.confidence` | NUMERIC | 抽取置信度 |
| `doc.error_count` | NUMERIC | 校验错误数 |

代码与 UI 操作：sibling `doc-workflow` → [`docs/zh/LANGFUSE.md`](../../../doc-workflow/docs/zh/LANGFUSE.md) · [`scores.py`](../../../doc-workflow/python-service/scores.py)。

更深样板（Prompt / Dataset / Experiment，**非本 Stage 重做**）：  
[`PHASE2_LANGFUSE_ADDENDUM.md`](../../../doc-workflow/docs/zh/PHASE2_LANGFUSE_ADDENDUM.md)。

---

## 怎么验收

```bash
# 1) 安装级（可选）
./scripts/bootstrap.sh up --profile langfuse

# 2) doc sidecar 配 LANGFUSE_PUBLIC_KEY + SECRET（接入）
# 3) kit 薄断言
python3 scripts/smoke_kit_llm_ops.py
```

| 情况 | 期望 |
|------|------|
| `/health.langfuse=skipped`（无密钥） | **诚实 skip**（同 D7；非失败） |
| `configured` + 金路径 | 响应含 `langfuse_scores`（ok 或可解释 skip）；UI 可按 score / metadata 过滤 |
| 闸门 | 仍 `shadow`；不因 score 阻断 Sheets/post |

---

## 非目标（P2-5）

完整 dataset 评测平台、多租户 prompt IDE、Helicone 替换、在 ecom/crm 再实装一套三件套。

---

## Review-P2-5

- [x] 安装 ≠ 接入写清
- [x] score 与 `correlation_id` / `trace_id` 关联写清
- [x] 外链 doc 更深样板；本 Stage 不重做
- [x] 默认 shadow；无强制阻断业务
