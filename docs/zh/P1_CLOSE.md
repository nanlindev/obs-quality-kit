# P1 收尾说明（Stage 9）

| 项 | 值 |
|----|-----|
| 状态 | **P1 完成**（MVP-1 = 验收层 A + B 全量 smoke 绿） |
| 日期 | 2026-09-16 |
| 成片 | **未剪**；**成片 = Phase-2 全部验收通过之后** |
| 下一阶段 | **Phase-2 进行中** — [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md)（P2-0 已写；自 P2-1 起实施） |

英文版要点同下；对外短述见根 [README](../README.md)。

## 回归命令

```bash
# 栈已 up（建议 full）时：
python3 scripts/smoke_kit_p1.py

# 仅静态（不含装栈/金路径）：
python3 scripts/smoke_kit_p1.py --static-only
```

本轮已跑通：`base` / `metrics` / `langfuse` / `full` + `smoke_kit_doc_path --live`（含 `smoke_doc_primary`）+ contract / facade / docs。

## 已知 WARN（P1 收口时；P2-1 后）

- ~~Langfuse sibling 浮动 tag / untagged MinIO~~ → **P2-1 已钉扎**（见 [IMAGE_PIN](IMAGE_PIN.md)）
- doc `/health.langfuse=skipped` 时 D7 跳过（未配 PK/SK 属预期；见 [DEMO_RUNBOOK](DEMO_RUNBOOK.md)）
- ≤8GB 主机勿长期挂 `full`

## Phase-2 入口

正式范围与 Stage 表：[PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md)。

PRD §15 / §22 已链到该 Addendum。分解计划：`obs_kit_phase2_ccd847de.plan.md`。
