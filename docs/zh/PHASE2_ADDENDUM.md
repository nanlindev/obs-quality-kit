# Phase-2 Addendum（OBS Quality Kit）

| 项 | 值 |
|----|-----|
| 版本 | 0.2-p2-smoke-green |
| 父文档 | [PRD.md](PRD.md) §15 / §22 |
| 分解计划 | `~/.cursor/plans/obs_kit_phase2_ccd847de.plan.md` |
| 前置 | [P1_CLOSE.md](P1_CLOSE.md) — A+B smoke 绿 |
| 收口 | [P2_CLOSE.md](P2_CLOSE.md) — P2-7 回归绿 |
| 成片闸门 | **成片 = P2-8**（P2-0…P2-7 已绿；中期禁止剪 75s） |

英文版：[../en/PHASE2_ADDENDUM.md](../en/PHASE2_ADDENDUM.md)

**本 Addendum 为增量。** 不整本重写 PRD；定位/L0–L3/Scheme B/shadow 默认不变。

---

## 1. 与 P1 的关系

| P1 已交付 | P2 增量 |
|-----------|---------|
| Bootstrap + O+J；profiles `base`/`metrics`/`langfuse`/`full` | 钉扎 P1 WARN；profile `loki` |
| 契约 + facade + **doc** 薄 adapter | **ecom** / **crm** 薄 adapter（同模式） |
| 手册包 + 分镜草稿（未拍） | 通用 app 指南；薄 LLM Ops；全绿后成片 |
| `smoke_kit_p1.py` | `smoke_kit_p2.py`（回归包） |

模式继续对齐 [DOC_ADAPTER.md](DOC_ADAPTER.md)：**不搬仓**；垂直只 env/health/闸门/互链；kit 侧 smoke + 手册。

---

## 2. 范围（In-scope）

| Stage | 内容 | 成片前必须绿？ |
|-------|------|----------------|
| **P2-0** | 本文 + PRD 链接 | ✅（文档） |
| **P2-1** | Langfuse/MinIO 钉扎（消化 P1 B20 WARN） | ✅ |
| **P2-2** | ecom 薄 adapter + `smoke_kit_ecom_path.py` | ✅ |
| **P2-3** | crm 薄 adapter + `smoke_kit_crm_path.py` | ✅ |
| **P2-4** | Loki profile（独立；可与 metrics 同开）+ smoke | ✅ |
| **P2-5** | 薄 LLM Ops（score/关联文档；优先 doc+L） | ✅ |
| **P2-6** | `GENERIC_APP_ADAPTER`（Frappe/WP/普通服务指南，**无实装**） | ✅ |
| **P2-7** | `smoke_kit_p2.py` + `P2_CLOSE` + 分镜补 ecom/crm/Loki 一闪 | ✅ |
| **P2-8** | 完整版 + 短版成片 | ✅（闸门最后一步） |

**P2「全部完成」定义：** P2-0…P2-7 验收绿 **且** P2-8 成片入库。

---

## 3. 非目标（本 P2 明确不做）

- Frappe / WordPress **代码实装**（仅指南）
- Tempo / Sentry / K8s / 社交垂类
- 重做垂直业务金路径或把 bootstrap/G+P 逻辑叉进 ecom/crm
- 把质量闸门默认改成 `block`
- P2 中期剪 Fiverr 75s / 对外成片
- 完整 dataset 评测平台、多租户 prompt IDE、Helicone 替换（P2-5 边界）

---

## 4. 工程约定（写死，防分叉）

| 主题 | 约定 |
|------|------|
| Adapter | 对齐 doc：`OBS_QUALITY_GATE_MODE`、health 暴露 Scheme B + 闸门字段、双语 `*_ADAPTER.md`、kit smoke |
| Loki | **独立** profile `loki`；可与 `metrics` 同开；**不**默认塞进 `full`（8GB 勿与 full 长期同挂） |
| LLM Ops | 安装 Addon vs 接入 Addon 仍分清；默认 shadow |
| 镜像 | 对齐 [IMAGE_PIN.md](IMAGE_PIN.md)；P2-1 消 MinIO/浮动 major WARN |
| 成片 | 节拍见 [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md)；口播须含 `trace_id`、Base+Addon、非低价全家桶 |

---

## 5. 验收总表（摘要）

| Stage | 期望 |
|-------|------|
| P2-0 | 本文列出 Stage；成片=P2 全绿后；PRD 已链 |
| P2-1 | `smoke --profile langfuse|full` 绿；无可审计 `latest`（或登记例外） |
| P2-2/3 | 垂直 health + Jaeger/`trace_id` + shadow；仓独立 |
| P2-4 | 至少一条可查日志（或文档化探针）；不改 `contract/` |
| P2-5 | 配 L 时可见 score/标注；未配 skip |
| P2-6 | 读者能自估工时；诚实无实装 |
| P2-7 | P2 一键/顺序全绿；P1 不回退 |
| P2-8 | 完整版 + 短版两支入库 |

细步与 Review 见分解计划；每步未绿不进下一步。

---

## 6. 状态流转

| 状态 | 含义 |
|------|------|
| `0.2-p2-planning` | Addendum 已写 |
| `0.2-p2-implementing` | 自 P2-1 起实施中 |
| `0.2-p2-smoke-green` | P2-7 绿、成片前（**当前**） |
| `0.2-p2-complete` | 含 P2-8 成片 |

P2-7 通过后把本页与 PRD 表头改为 `smoke-green`。
