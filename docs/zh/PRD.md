# OBS Quality Kit — 产品需求文档

| 项 | 值 |
|----|-----|
| 版本 | 0.2-p2-smoke-green |
| 仓 | `obs-quality-kit`（独立新仓） |
| 定位 | 可售卖的 **OBS 装栈 + 质量横切层**；重插件 / 薄 n8n 门面；非垂直业务 SaaS |
| 运行时 | 公用 `platform-n8n`；OTEL + Jaeger 为底座；可选 Langfuse、Grafana+Prometheus |
| 文档 | `docs/zh/` 自用；`docs/en/` 对外 |
| 注释 | 关键脚本 / 契约字段 / 节点说明使用英文 |
| 状态 | **P2 implementing**（[PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md)）；P2-1 钉扎进行中/完成；成片仍锁 P2 全绿后 |

英文版：[docs/en/PRD.md](../en/PRD.md)

---

## 1. 目标

作品集 / Upwork（主）/ Fiverr（Base+Addon）/ LinkedIn / GitHub：交付一套可引导安装的观测与质检横切能力，使自动化（默认演示：`doc-workflow`）具备：

- **可装**：一键/引导脚本起 Docker 网络与所选 OBS 组件（半自动预检 + 手册）
- **可观**：链路（Jaeger）、指标（Grafana+Prometheus，可选）、LLM（Langfuse，可选）
- **可质检**：与编排器解耦的质量契约（IDs、闸门、trail 钩子）；默认 shadow，不默认闸死业务
- **可演示**：薄 n8n facade + doc 一条金路径；**成片放在 Phase-2 全部做完之后**（P1 只要求全量 smoke 绿）

**MVP-1 完成定义 = 验收层 A（装栈）+ 验收层 B（doc 一条金路径）**，二者缺一不可。

远期（非 MVP）：若足够通用，可逐步替代日常「手搓 platform + 多 OBS 仓」的底座习惯；**第一版不追求一次性替换**现有四垂直仓。

---

## 2. 定位

| 是 | 不是 |
|----|------|
| OBS bootstrap + profile 化后端 | 社交 Media Command Center / 舆情 BI SPA |
| 质量契约 + 垂直薄 adapter | 再做一个「功能最多」的 n8n 垂直模板 |
| 重插件（脚本/compose/契约/smoke） | 重 n8n 画布逻辑 |
| 1 个 Gig Base + Addons | 用 L / G+P / full 硬映射 Fiverr 三档套餐 |
| 默认可接到 n8n + doc | 承诺任意 ERP/WP 即插即用（见扩展） |

**差异化：** 规则与 triage、OBS 组合可交付、更深 Langfuse/质检 —— 不是堆更多公域连接器。

---

## 3. 非目标（MVP-1）

- 社交多平台监听、自动公域回复、情感分析大盘
- Loki / ELK / Sentry / Tempo 实装（**可扩展插槽预留**，见 §18）
- Frappe / WordPress / 任意 ERP 的实装 adapter（仅指南占位）
- K8s / Swarm / 纯托管 PaaS 安装器
- 自建运营 Web 后台、「为了日志好看」的中台
- 中期 / MVP 未完成时剪 Fiverr 75s 或对外成片
- 平台级交付按单一超低价 Basic「全家桶交钥匙」话术
- 脚本静默 `latest` 升级；无鉴权公网裸奔 OBS UI
- 将 bootstrap / G+P 大段逻辑分叉进 `crm`/`ecom`/`doc`/`platform` 四仓

---

## 4. 架构分层（L0–L3）

```text
L0  采集总线：OTEL Collector +（可选）Prometheus scrape 配置
L1  后端 profile：Jaeger（底座）/ Langfuse / Grafana+Prometheus / 未来 Loki…
L2  质量契约：correlation_id、trace_id、闸门与 trail 的最小字段/HTTP 约定（与编排器无关）
L3  适配器：薄 n8n facade、doc-workflow（MVP）、将来 ecom/crm/Frappe/WP…
```

```text
obs-quality-kit (本仓)
  ├── bootstrap + profiles + smoke A
  ├── quality contract (库/HTTP/文档，非 n8n-only)
  └── thin n8n facade JSON
        │
        ├── platform-n8n（公用，不搬进本仓）
        ├── OTEL → Jaeger（底座）；可选 → Langfuse；可选 G+P
        └── doc-workflow（薄 adapter，仓仍独立）
```

| 层 | 职责 |
|----|------|
| Bootstrap | 预检、选 profile、起网络/容器、写 `.env`、幂等重跑、故障提示 |
| L1 OBS | 按 profile 组合后端；镜像钉扎；UI 默认不公网裸奔 |
| L2 契约 | Scheme B IDs；shadow/block 闸门开关；trail 钩子约定 |
| L3 n8n | 门面工作流：展示与转发，逻辑尽量少 |
| L3 doc | 现有 sidecar/流程服从契约；扩展 smoke 观测断言 |

**红线：** A 层验收 **不得**假设必须有 n8n；n8n 是默认 L3 演示适配器。质检核心禁止只活在无法复用的 n8n Code 节点里。

---

## 5. 仓库拓扑与同机共存

```text
obs-quality-kit/     # 本产品：脚本、profiles、契约、facade、smoke、手册
platform-n8n/        # 公用 n8n
otel-collector-stack / jaeger-stack / langfuse-stack
                     # MVP 允许脚本编排现有仓；中长期可收编进 kit compose
doc-workflow/        # 独立垂直；仅薄 adapter
ecom-workflow/ crm-workflow/   # Phase-2 adapter
```

- 本仓自洽：**根目录 `docker-compose.yml` wrapper + `docker/compose.yml`**（符合 `platform-n8n` Docker 标准），便于 `dup`/`ddown`。
- 固定 **项目前缀 / compose project name / label**，避免与现有栈误刮、误连。
- 网络约定：加入现有 `proxy_network` / `n8n_platform`（名称以 `DOCKER_STANDARDS` 与安装时探测为准）；缺失则创建或中止并提示。

---

## 6. 工程 Profile 与商品形态

### 6.1 工程组合（安装/验收用）

| 名称 | 组成 | 说明 |
|------|------|------|
| 底座（不可关） | OTEL Collector + Jaeger | Base 交付必含 |
| `langfuse` | 底座 + Langfuse | 有 LLM 时 |
| `metrics` | 底座 + Grafana + Prometheus | G 与 P **绑定**，不拆卖 |
| `full` | 底座 + Langfuse + G+P | 作品集全家桶演示 |

### 6.2 商品形态（Gig / 报价）

**唯一主档 Base + Addons**（不把工程三档硬映射成 Fiverr 三 package）。

| SKU | 含什么 | 不含 |
|-----|--------|------|
| **Base** | O+J、bootstrap、手册、smoke A、暴露面默认安全 | 改客户业务代码；不默认 G+P/L |
| **Addon: Metrics (G+P)** | metrics profile、一页 infra 看板、对应 smoke | 业务自定义告警大全 |
| **Addon: Langfuse 安装** | L UI 起来、collector 可接、安装级 smoke | 完整 LLM Ops / 改 sidecar |
| **Addon: 质检或 LLM 接入（1 流）** | 契约接到一条流（MVP=doc 金路径）+ 深 smoke | 无限改需求；第二条流另计 |
| **Addon: 维护/升级** | 改镜像 pin、回归 smoke | 自动 latest |

定价数字实施期再定；原则：平台级能力 **不得**按「薄教程 Basic 全包」售卖。

---

## 7. 质量契约（L2，语言无关）

从 `doc-workflow` 抽取**最小集**（实施时以现网代码+手册为准校准字段名）：

| 字段/能力 | 要求 |
|-----------|------|
| `correlation_id` | 业务 UUID；入口分配；审计 / trail / 卡片 |
| `trace_id` | W3C/OTEL hex；**Jaeger 粘贴用**；响应与卡片展示 |
| `traceparent` | 传入 sidecar / 下游；span attribute 带 `correlation_id` |
| 闸门模式 | `shadow`（默认）\| `block`（显式开启）；test/production 分离 |
| Processing trail | 可按 `correlation_id`（及可选 `trace_id`）查询阶段事件 |
| Langfuse 钩子 | 有 LLM 时：generation / 可选 score；无 LLM 可跳过 L |

契约真相源 = **本仓字段表 +（若有）小型库/HTTP**；n8n 节点名不是唯一真相。

**不在契约 MVP：** 完整 dataset 评测平台、多租户控制面 UI。

---

## 8. 薄 n8n Facade（L3）

- 目的：作品集「好看的入口画布」；编排尽量 `Execute Workflow` / HTTP 到契约与垂直。
- 禁止变成 god-workflow；Error / Keepalive 若需要则遵循作品集横切（可复用 platform 习惯）。
- 凭证占位 + 导入后重绑；关键节点英文注释。

---

## 9. doc 金路径（验收层 B）

- 在 `doc-workflow` 做**薄 adapter**（env、少量 sidecar、文档链接），**不搬仓**。
- 金路径对齐现有主信任路径（Webhook 样例 → 处理 → 可观测 ID）；扩展断言：
  - Jaeger 能用 `trace_id` 查到
  - 若启用 L：Langfuse 可见对应轨迹（深度按 Addon）
  - trail / 卡片可讲清阶段（若已有则复用）
- 回归：延伸或并列 `smoke_doc_primary` 思路的 kit 侧 / doc 侧 smoke（见 §16）。

ecom / crm：**Phase-2**，PRD 只预留「同类 adapter 步骤」。

---

## 10. 错误处理与横切（适用于 facade / 接入流）

接入 doc 或 facade 时沿用作品集约定（摘录为验收项）：

- 第三方 / DB / sidecar：`continueErrorOutput` + **已接线** error handler；禁止悬空 error 口
- 工作流 Error Trigger：导入后**手工重绑**
- Code `mode`：聚合用 `runOnceForAllItems`，逐条用 `runOnceForEachItem`
- test/production：出站跳过带明确 skip status
- Keepalive：至少 sidecar/collector 或关键依赖 `/health` 可纳入（kit 或 doc 侧文档化）

---

## 11. AI / Langfuse

- **安装 Addon**：栈与 ingest 通即可。
- **接入 Addon**：改代码（sidecar prompt/score/闸门）属深度；脚本不自动完成。
- Prompt 版本化优先落在垂直仓；kit 契约只要求可关联 `trace_id` / `correlation_id`。
- 结构化 LLM 输出字段（如 `fallback_used`）由垂直 PRD 约束；kit 要求闸门可消费这些信号。

---

## 12. 可观测性（OBS）

| 信号 | 工具 | MVP |
|------|------|-----|
| Traces | OTEL → Jaeger | 底座必有 |
| Metrics | Prometheus + Grafana | Addon；默认刮 **容器/cAdvisor 级** |
| LLM | Langfuse | Addon |
| 业务流水 | Processing trail | 经契约/doc 复用 |
| Logs 后端 | Loki 等 | 非 MVP，L1 插槽 |

指标与链路互补，**不互斥**。业务对错仍靠规则 / smoke / trail，不只靠 Grafana。

`NO_PROXY`：延续 platform 对 collector / 内部服务名的习惯，装栈文档写清。

---

## 13. 安全（专章）

| 主题 | MVP 默认 |
|------|----------|
| UI 绑定 | Grafana / Prom / Jaeger UI / Langfuse **默认不公网裸奔**（`127.0.0.1` 或仅内部网络）；公网 = 反代 + 鉴权（手册） |
| 初始密钥 | Grafana/Langfuse 首次强密码（脚本生成或强制写入 `.env`）；禁止提交真 secret |
| 密钥落盘 | `.env` gitignore；smoke/日志不打印完整 secret |
| Scrape | 只刮约定目标；Docker socket 等风险在手册标明 |
| OTLP | 默认网络内；主机暴露须防火墙说明 |
| 闸门 | 默认 **shadow**；`block` 显式开；防闸死 ERP/真业务 |
| 数据责任 | Langfuse 等可能含业务/LLM 内容 → 保留与访问由客户负责（诚实声明） |

**安全 smoke（最低）：** 关键 UI 未在无鉴权 `0.0.0.0` 暴露（或明确 lab-only 配置）；`.env.example` 无真 secret。

---

## 14. 安装运维（褐地、幂等、支持矩阵）

| 主题 | MVP 默认 |
|------|----------|
| 褐地 | 端口/同名栈冲突 → **采用现有 endpoint / 换端口另起 / 中止**；禁止静默双开互抢 |
| 半失败 | 预检失败不拉镜像；失败后残留提示 + `down`/清理；**二次执行幂等** |
| 支持矩阵 | **仅** Docker Compose（Linux VPS、OrbStack/Docker Desktop 同类） |
| 磁盘 | 预检空间；full/Langfuse 保留建议；勿在 8GB 演示机长期挂 full |
| 镜像 | **禁止 `latest`**；钉不可变 tag 或 digest；升级 = 维护 Addon |
| 回滚 | 文档级 compose down / volume 策略；不承诺跨大版本一键迁移 |
| 反代 | NPM / nginx / Caddy 手册；其它面板升级或自理 |

兼容性策略总口径：**半自动预检 + 手册**。

---

## 15. 功能模块：MVP vs Phase-2

| 模块 | MVP-1 | Phase-2+ |
|------|-------|----------|
| Bootstrap + 底座 O+J | ✅ | 增强预检 |
| Profile `langfuse` / `metrics` / `full` | ✅ | — |
| G+P 默认容器指标 + 一页看板 | ✅ | 业务指标、告警规则 |
| 质量契约最小集 | ✅ | 更多闸门策略 |
| 薄 n8n facade | ✅ | 美观迭代 |
| doc 薄 adapter + 金路径 | ✅ | — |
| 细 smoke（含 bootstrap 故障矩阵） | ✅ | 扩负例 |
| ecom / crm adapter | — | ✅ |
| Loki profile | — | ✅（插槽先有文档） |
| Frappe/WP 实装 | — | 指南 + 付费定制 |
| 演示成片 | 分镜草稿即可（不拍） | **P2 全部完成后**再剪完整版+短版 |

Phase-2 默认写 **Addendum**，不整本重写 PRD；除非定位/架构大变。

**现行 Addendum：** [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md)（P2-0…P2-8；**成片 = P2 全绿后**）。

---

## 16. 细 Smoke 与故障矩阵（专章）

**原则：** 每个实施大步结束必须有可重复验收；bootstrap **最细**。能稳定自动的进脚本；不能的进手册手测清单。

### 16.1 Smoke 入口（目标形态）

- `scripts/smoke_kit_bootstrap.py`（或等价）：按 profile 跑 A
- `scripts/smoke_kit_doc_path.py`（或扩展 doc 既有 smoke）：跑 B
- 空面板 / 无 span / 无 scrape = **失败**

### 16.2 Bootstrap 故障与场景矩阵（验收表）

| # | 场景 | 期望 |
|---|------|------|
| B1 | Docker daemon 未起 | 预检失败，可读错误 |
| B2 | Compose/引擎版本过旧 | 预检失败，提示最低版本 |
| B3 | 权限不足 | 预检失败 |
| B4 | 磁盘不足 | 预检失败或强警告（Langfuse 场景） |
| B5 | 端口占用（4317/4318、UI 端口等） | 检测 → 换端口 / 采用现有 / 中止（策略写死） |
| B6 | `proxy_network` 缺失 | 创建或中止并提示 |
| B7 | 网络名冲突 | 明确策略，不静默踩踏 |
| B8 | 褐地已有 Jaeger/L/G | 三选一，不双开互抢 |
| B9 | 预检失败 | **不**开始 pull |
| B10 | 拉起中失败 | 残留提示 + 清理命令 |
| B11 | 二次执行同一 profile | 幂等成功 |
| B12 | 中断后再跑 | 可恢复或可清理后成功 |
| B13 | Base 后再加 Addon | 成功，不拆底座 |
| B14 | `metrics` 金路径 | Prom 有目标；Grafana 有线 |
| B15 | `langfuse` 金路径 | Web 可开；与 collector 配置一致 |
| B16 | `full` | B14+B15 |
| B17 | 底座 Jaeger | 至少一条 demo/平台 span 或文档化探针 |
| B18 | 故意错误 endpoint / 停容器 | smoke **失败**且指向明确 |
| B19 | 安全绑定 | 见 §13 安全 smoke |
| B20 | 镜像非 latest | compose/锁文件可审计 |

### 16.3 契约 / facade / doc B

| # | 场景 | 期望 |
|---|------|------|
| D1 | doc `/health` | 绿 |
| D2 | 主信任路径样例 | 成功终态或明确 skip |
| D3 | 坏样本 / mismatch | 按 doc 规则失败或进审 |
| D4 | 重复投递 | 幂等 / duplicate skip |
| D5 | ID 贯穿 | 响应/卡片/`trail` 含 correlation + trace |
| D6 | Jaeger | `trace_id` 可查 |
| D7 | Langfuse（若启用） | 可见对应记录 |
| D8 | 观测断链负例 | 断言失败可读 |
| D9 | 闸门 shadow | 不默认阻断业务写入 |

---

## 17. 横切验收清单（可勾选）

- [ ] L0–L3 边界清晰；契约无「唯 n8n」假设
- [ ] Profile 注册表可扩展（防假扩展：有「如何新增 profile」文档，即使尚未做 Loki）
- [ ] Base / Addons 边界与工程 profile 对照表一致
- [ ] Scheme B：`correlation_id` + `trace_id`；Jaeger 用 trace_id
- [ ] 闸门默认 shadow；block 显式
- [ ] UI 默认不公网裸奔；密钥不进 git
- [ ] 镜像钉扎；无静默 latest
- [ ] 褐地三选一；bootstrap 幂等；半失败可清理
- [ ] 支持矩阵仅 Compose
- [ ] A smoke 矩阵 §16.2；B smoke §16.3
- [ ] doc 薄 adapter；逻辑不进四仓分叉
- [ ] facade 薄；凭证重绑说明
- [ ] 双语文档；关键英文注释
- [ ] 样例无真客户 PII
- [ ] P1 全量 smoke 绿即可收 P1；成片仅 P2 收尾；分镜可先写标注未拍

---

## 18. 扩展性

### 18.1 新增 L1 后端（例：Loki）

1. `profiles/<name>/`：compose 片段、端口、依赖  
2. 注册表项 + 预检 + smoke 金路径一行  
3. Collector pipeline（若需要）  
4. Addon 价目与手册  
5. **不**改 L2 字段语义  

MVP 不实现 Loki；未注册 profile = 手册「升级/定制」。

### 18.2 非 n8n 应用（Frappe / WordPress / ERP）

| 能力 | 可否 | 说明 |
|------|------|------|
| G+P | 能 | 与业务无关 |
| O+J | 能 | 应用打 OTLP 或旁路 agent |
| Langfuse | 有 LLM 才有意义 | |
| 质量契约 | 能 | 需 L3 adapter（hook/middleware/worker） |
| n8n facade | 不必 | |

对外可说「可接到自有应用」；MVP **只交付** n8n + doc。通用适配指南见 Phase-2：**[GENERIC_APP_ADAPTER.md](GENERIC_APP_ADAPTER.md)**（**无** Frappe/WP 实装；付费定制）。

---

## 19. 交付物

| 交付物 | 说明 |
|--------|------|
| 本仓代码与 compose profiles | 钉扎镜像 |
| `scripts/bootstrap*` | 交互/半自动 |
| smoke 脚本 | A + B |
| `docs/en` + `docs/zh` | INSTALL、SECURITY、CREDENTIALS、扩展指南、故障手册（症状索引） |
| 反代手册 | NPM / nginx / Caddy |
| 薄 facade 工作流 JSON | 导入 platform-n8n |
| doc adapter 说明与补丁边界 | 链到 `doc-workflow` |
| DEMO_RUNBOOK + 分镜草稿 | P1 可写草稿；**成片 = Phase-2 收尾闸门** |
| `.env.example` | 无真 secret |

---

## 20. 建议分解顺序（仅 PRD 批准后）

每步必须带 **Given/When/Then 或命令级验收**；大阶段后 **Risk Review**（密钥、暴露面、幂等、PRD 漂移、可讲解性）。

1. 仓骨架：compose wrapper、网络约定、镜像钉扎策略、`.gitignore`  
2. Bootstrap 预检 + 底座 O+J + §16.2 核心行（B1–B12, B17, B19–B20）  
3. Profile `metrics` + 看板 + B14  
4. Profile `langfuse` + B15；`full` = B16  
5. 质量契约文档 + 最小实现（库或 HTTP）+ 语言无关字段表  
6. 薄 n8n facade + 导入说明  
7. doc 薄 adapter + §16.3  
8. 故障手册（症状索引）+ 反代手册 + 安全声明  
9. 双语文档对齐；分镜草稿（不拍摄）  
10. **P1 收尾：** 全量 smoke 绿（**不剪片**）  
11. **Phase-2**（另开 Addendum）：ecom/crm 等 → 全绿后 **再剪** 完整版 + 短版  

---

## 21. 交付原则与 GTM

- Upwork + 作品集为主；Fiverr = Base + Addons，尽力而为  
- 简历/LinkedIn：讲「可观测 + 质检横切 + 按需加装」，不堆组件名当套餐  
- 诚实声明：非会计替代、非任意布局 100%、非 GDPR 成品、非低价交钥匙全家桶  
- 调试成本控制：少默认组合、A/B 分层、每步细 smoke  
- Human vs agent：产品边界你定；机械实现与 smoke 代理执行  

---

## 22. MVP vs Phase-2 边界

见 §15。Phase-2 范围与验收以 **[PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md)** 为准（增量：ecom/crm、Loki、告警/日志 profile、通用 app 指南、更深 LLM Ops、成片）。

---

## 23. 演示与视频

| 规则 | 定调 |
|------|------|
| 中期剪 75s | **禁止** |
| P1 结束标准 | MVP-1（A+B）全量 smoke 绿；**不剪成片** |
| 成片时机 | **Phase-2 全部验收通过之后** |
| 产出 | **完整版**（YouTube 级，约 2–3 min）+ **短版**（Upwork ≤90s / Fiverr ≤75s 可同一短版剪裁） |
| 拍摄方式 | 剪辑叙事；不靠直播四仓马拉松 |
| 分镜 | P1 Stage8：[`assets/demo-shot-list.md`](../../assets/demo-shot-list.md)，标注「未拍 / 待 P2 收尾」 |
| 手跑讲法 | [DEMO_RUNBOOK](DEMO_RUNBOOK.md) |

**主信任路径（短版）：** Bootstrap 选装 → 面板红绿 / Jaeger 一条 → doc 金路径 + `trace_id`（P2 可加 ecom/crm 一闪）。  
**完整版加：** L0–L3、安全/暴露面、Addon 话术、trail/Langfuse、P2 适配亮点。

---

## 24. 风险与开放项（不挡 0.1 实施设计）

| 项 | 状态 |
|----|------|
| 对外营销名是否等于仓名 `obs-quality-kit` | P1 暂用仓名；上架前可改 |
| Addon 具体美元价 | **成片/上架前定**（成片 = Phase-2 结束后） |
| 第一版 OBS 是「编排现有三仓」还是「kit 内 compose 收编」 | **已定（P1）：** metrics 本仓收编；O+J+L 编排 sibling，文档已写清 |
| 8GB 机长期跑 full | 文档禁止；demo 短时允许 |

---

*0.2-p2-smoke-green — P2-7 回归绿；成片 = P2-8。*
