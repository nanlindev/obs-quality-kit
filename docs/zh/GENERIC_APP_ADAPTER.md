# 通用应用适配指南（P2-6）

如何把 **非 n8n / 非本仓垂直** 的应用接到 OBS Quality Kit 的 L0–L2。  
覆盖：**Frappe**、**WordPress**、**普通 HTTP/worker 服务**。

英文版：[../en/GENERIC_APP_ADAPTER.md](../en/GENERIC_APP_ADAPTER.md)

---

## 诚实边界（先读）

| 本页交付 | **未**交付（MVP / 本 P2） |
|----------|---------------------------|
| 清单式接入指南 + 工时自估 | Frappe / WP / ERP **产品级**实装、现成通用插件市场包 |
| 对齐 [DOC_ADAPTER](DOC_ADAPTER.md) 薄补丁思路 | 替客户改业务规则、做完整 ERP 集成 |
| **样例** [`examples/wp-sme`](../../examples/wp-sme/)（本地 SME WP） | 把样例当成「开箱即用 SaaS 插件」 |
| 可对外说「可接到自有应用（有试点）」 | 宣称任意远程 Woo/WP 已全测 |
需要落地实装 = **付费定制 / 深度交付**（见 [BASE_ADDONS](BASE_ADDONS.md) 接入 Addon）。  
样板垂直仍是 sibling `doc` / `ecom` / `crm` 薄 adapter，不是通用 SDK。

---

## 能力对照（PRD §18.2）

| 能力 | 能否接到自有应用 | 说明 |
|------|------------------|------|
| L0 网络 / 安全绑定 | 能 | 与业务栈无关；UI 默认 loopback + 反代 |
| L1 OTEL → Jaeger | 能 | 应用打 OTLP，或旁路 agent / sidecar |
| L1 Grafana + Prometheus | 能 | scrape exporter / cAdvisor；与业务无关 |
| L1 Loki（可选） | 能 | 日志进 Loki；见 [LOKI](LOKI.md) |
| L1 Langfuse | 有 LLM 才有意义 | 安装 ≠ 接入；见 [LLM_OPS](LLM_OPS.md) |
| L2 质量契约 | 能 | 需自写薄 adapter（middleware / hook / worker） |
| L3 n8n facade | **不必** | 非 n8n 应用可跳过 |

**禁止**为接新应用改 `contract/` 的 Scheme B / 默认 `shadow` 语义。

---

## 通用薄 adapter 清单（对齐 doc）

无论 Frappe / WP / 自研服务，推荐同一最小集：

1. **进程能出口 OTLP** → kit 的 `otel-collector:4318`（同 `proxy_network` 或可达地址）
2. **`OTEL_SERVICE_NAME`** 稳定可搜（Jaeger 服务名）
3. 请求链路透传 **`X-Correlation-Id`** + 可选 **`traceparent`**
4. 响应 / 日志暴露 **`correlation_id`** + **`trace_id`**（32 hex；Jaeger 只用后者）
5. 健康检查（或等价探针）返回：  
   `obs_quality_gate_mode`、`obs_quality_gate_blocks_writes`（默认 **shadow**）
6. 有 LLM 时：generation / 可选 score；metadata 带 `correlation_id`（见 [LLM_OPS](LLM_OPS.md)）
7. **不要**默认 `block`；质量失败只记录，除非客户明确要求

参考实现边界：[DOC_ADAPTER](DOC_ADAPTER.md) · [CONTRACT](CONTRACT.md)。

---

## Frappe

| 步骤 | 做法（指南级） | 粗估 |
|------|----------------|------|
| OTEL | 在 bench / Docker 服务加 OTLP env；或旁路 OpenTelemetry Collector agent | 0.5–1.5d |
| ID | 在 API / 白名单 hook 注入 `correlation_id`；背景 job 写入 docfield 或 log | 1–2d |
| 健康 / 闸门 | 自定义 whitelisted method 或站点健康页暴露 shadow 字段 | 0.5–1d |
| G+P | 仅起 kit `metrics`；可选 Frappe 进程 exporter | 0.5d |
| Langfuse | 仅当站点调 LLM；SDK 挂在调用处 | 1–3d（接入） |
| n8n facade | 通常跳过 | — |

**未交付：** Frappe app、hooks 补丁包、一键 bench 脚本。

---

## WordPress

| 步骤 | 做法（指南级） | 粗估 |
|------|----------------|------|
| OTEL | PHP 难原生 OTLP → 常用：**旁路**（web 服务器 access log → Promtail/Loki；或小 sidecar 代理） | 1–2d |
| ID | 插件 / mu-plugin：REST 入口生成 UUID；写 response header | 0.5–1.5d |
| 契约字段 | 自定义 REST `GET /obs-health` 返回闸门 + ID | 0.5–1d |
| G+P | kit metrics + 可选 WordPress 无关；关注主机/容器指标即可 | 0.5d |
| Langfuse | 仅 Woo / AI 插件调模型时才有意义 | 1–3d |
| n8n facade | 可选：WP webhook → n8n；非必须 | 另计 |

**未交付（产品级）：** 通用 WP 插件市场包、Woo/LMS 一键栈、PHP OTLP SDK。

### WP SME 试点（已落地样例）

kit 仓内 [`examples/wp-sme/`](../../examples/wp-sme/)：本地 **SME 营销站**（官方 WordPress 镜像，无 n8n / 无 Woo）。

| 已验证 | 仍属定制 |
|--------|----------|
| `proxy_network` + loopback `:8087` | Elementor / Woo / 会员课 |
| `GET /obs-health/` → `shadow` + `correlation_id` | PHP → Jaeger `trace_id` |
| Docker 日志 → kit Promtail → Loki（需 `up --profile loki`） | 远程生产 WP 硬化 |

```bash
./scripts/bootstrap.sh up --profile loki
cd examples/wp-sme && docker compose -f compose.yml up -d && ./install.sh
python3 scripts/smoke_kit_wp_sme.py
```

---

## 普通 HTTP / worker 服务

| 步骤 | 做法（指南级） | 粗估 |
|------|----------------|------|
| OTEL | `opentelemetry-instrument` / 官方 SDK → Collector | 0.5–1d |
| 契约 | middleware：读/写 Scheme B 头；`/health` 暴露闸门字段 | 0.5–1d |
| 金路径 smoke | 自写 1 条 happy path + kit 侧静态清单（照 ecom/crm smoke） | 0.5–1d |
| Langfuse | 有 LLM 再接；安装用 kit profile | 按 [LLM_OPS](LLM_OPS.md) |

最接近现成样板：本 monorepo 的 `doc` / `ecom` / `crm` Python sidecar。

---

## 工时自估怎么用

- 上表为 **单人熟悉 Docker + 目标栈** 的量级，含联调缓冲；不含客户业务规则重写。  
- 「安装」kit（base/metrics/langfuse）与「接入」应用是两笔账（[BASE_ADDONS](BASE_ADDONS.md)）。  
- 若要 **可演示金路径 + smoke 绿 + 手册**，按垂直再加 1–3d（对标 doc adapter）。  
- 超出清单（多租户、ERP 单据映射、完整评测平台）→ 单独报价，不在本指南范围。

---

## 建议验收（客户侧自检）

- [ ] Jaeger 能用 **`trace_id`** 搜到应用 span  
- [ ] 同一请求的 `correlation_id` 出现在日志 / 业务表 /（若有）Langfuse metadata  
- [ ] 健康探针 `obs_quality_gate_mode=shadow` 且不阻断写路径  
- [ ] 未向公网裸奔 OBS UI（[SECURITY](SECURITY.md) / [REVERSE_PROXY](REVERSE_PROXY.md)）

kit **不会**因本指南自动生成 Frappe/WP 仓库。

---

## Review-P2-6

- [x] 指南为主；**产品级** WP 插件未交付  
- [x] 写明付费定制 / 未交付  
- [x] 读者可按表自估工时  
- [x] 默认 shadow；不改 contract 语义  
- [x] 可选：本地 WP SME 试点 `examples/wp-sme/`（日志 + `/obs-health`）
