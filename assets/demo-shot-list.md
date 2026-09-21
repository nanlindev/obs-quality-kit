# OBS Quality Kit — 分镜（Stage 8 / P2-8）

| 项 | 值 |
|----|-----|
| 日期 | 2026-09-18 |
| 状态 | 素材已采；**成片未入库（未拍成片 / unfilmed in-repo）** · **待 P2-8** 剪辑封版 |
| 封面 | **架构图**（与片头同图） |
| 口播 | **完整版** [demo-vo-full.md](demo-vo-full.md) · **短版** [demo-vo-short.md](demo-vo-short.md) |
| Fiverr | **可卖**（Base+Addons，尽力而为）；主战场 Upwork；禁止「Basic=全家桶」 |
| 架构图 | [demo/architecture-obs-kit.svg](demo/architecture-obs-kit.svg) · [demo/architecture-obs-kit-hero.png](demo/architecture-obs-kit-hero.png) |
| 作业单 | [docs/zh/P2_8_FILM.md](../docs/zh/P2_8_FILM.md) · 入库 [demo/videos/README.md](demo/videos/README.md) |
| 成片闸门 | **成片 = Phase-2（P2-8）之后**；mp4 不进 git 直至封版 |

---

## 剪辑原则

| 规则 | 做法 |
|------|------|
| 主故事 | 架构 → 终端 help → Grafana → Prom → Jaeger（展 span）→ health → Loki（滚日志） |
| 节奏 | 画面约 73s + 口播 ~75s；按 [demo-vo-full.md](demo-vo-full.md) beat map 对齐，可微持 |
| 不拍 | n8n / doc 业务操作；空 Langfuse |
| 必落点 | 非 compose 全家桶 · My stack · `trace_id` ≠ correlation · shadow · Base+Addon |

---

## 1. 完整版 — 实拍参考时间（可伸缩）

| # | 参考 | 画面 | 动作 | 口播 |
|---|------|------|------|------|
| Y01 | 0:00–0:05→可拉~15s | 架构图 / 封面 | 静帧 | **高** |
| Y02 | 0:05–0:12 | 终端 `-h` + `up -h` | 无需再敲 | 低 |
| Y03 | 0:12–0:23 | Grafana infra | 可慢扫图例 | 中 |
| Y04 | 0:23–0:33 | Prom targets | 无需点 | 低 |
| Y05 | 0:33–0:45→可拉~25s | Jaeger | **展开 span** | **高** |
| Y06 | 0:45–0:54 | `/health` JSON | 停 shadow 字段 | 中 |
| Y07 | 0:54–1:13→可拉 | Loki Explore | **滚动日志** | 中 |
| Y08 | 尾 3–5s | CTA 叠 Loki/黑场 | — | 中 |

成片：**一支 ~75s**（Fiverr 上限友好；Upwork/封面同片）— 仓库内仍标 **未拍成片 / unfilmed** 直至 `demo/videos/` 入库。

### P2 闪切（完整版附加 / 短版）

| # | 用途 | 画面 |
|---|------|------|
| **Y-P2a** | 完整版闪切 | ecom / crm adapter 文档或 smoke 一行（非业务重演） |
| **Y-P2b** | 完整版闪切 | Loki Explore 滚日志（可与 Y07 合并） |
| **S-P2** | **短版**闪切 | 架构图 → Grafana/Jaeger 各 1 拍 → CTA |

---

## 2. 明确不说

- 垂直业务重演（链旧成片）
- 「就是 compose 主流观测站」当卖点
- WP 万能 / 低价全家桶 / 替代会计

---

## 变更

| 日期 | 说明 |
|------|------|
| 2026-09-18 | 实拍分镜入库；VO 按口播主导重写；封面=架构图；无 Langfuse |
| 2026-09-18 | 站台向初改（拍前） |
| 2026-09-17 | P2-7 / P2-8 prep |
