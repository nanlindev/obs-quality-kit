# 演示 Runbook（DEMO_RUNBOOK）

手跑「可讲」路径；**不是**成片脚本。成片节拍见 [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md)。

英文版：[../en/DEMO_RUNBOOK.md](../en/DEMO_RUNBOOK.md)

成片作业（P2-8）：[P2_8_FILM.md](P2_8_FILM.md) · VO [`demo-vo-full.md`](../../assets/demo-vo-full.md) / [`demo-vo-short.md`](../../assets/demo-vo-short.md) · 入库 [`assets/demo/videos/`](../../assets/demo/videos/README.md)

---

## 硬规则

| 规则 | 说明 |
|------|------|
| P1 | 全量 smoke 绿即可收；**不剪成片** |
| **成片** | **= P2-8（Phase-2 成片闸门）**；P2-0…P2-7 smoke-green 见 [P2_CLOSE](P2_CLOSE.md) |
| 分镜 | 含 Y-P2a/b、S-P2；镜头一律 **未拍** 直至两支成片入库 |
| ecom/crm/Loki 一闪 | 见分镜 Y-P2a / Y-P2b |
| 录屏 | **本机人工**；AI 只交付 VO/作业单，不虚标已拍 |

---

## 5 分钟可讲路径（本机）

```bash
# 0) 网络
../platform-n8n/scripts/ensure-networks.sh

# 1) Base 或 metrics
cp -n .env.example .env
./scripts/bootstrap.sh up --profile metrics
python3 scripts/smoke_kit_bootstrap.py --profile metrics

# 2) UI（默认 loopback）
open http://127.0.0.1:3001          # Grafana uid=obs-kit-infra
open http://127.0.0.1:16686         # Jaeger — 用 trace_id 搜

# 3) Doc 金路径 B（sidecar 已起时）
python3 scripts/smoke_kit_doc_path.py --live
# 或 doc 仓：python3 scripts/smoke_doc_primary.py
```

讲解顺序建议对齐短版分镜：装栈 → 面板/Jaeger → doc + `trace_id`。

| 检查点 | 期望 |
|--------|------|
| Prom targets | cadvisor / prometheus UP |
| Grafana | 有线（Mac 上主机盘可能偏少，容器线即可） |
| Jaeger | health 或 doc 响应里的 **trace_id** 可打开 |
| `/health` | `obs_quality_gate_mode=shadow` |
| Langfuse（D7） | `/health.langfuse=configured` 才深查；**`skipped` = 未配密钥，诚实跳过**（非失败） |
| Facade（可选） | n8n 导入后 Manual Execute 见 Scheme B + health |

---

## 与垂直 demo 的关系

- **doc-workflow** 业务成片 / 分镜仍在 doc 仓；本 kit 讲「横切怎么装、怎么追」
- Facade **不**替代 Doc Process / Post
- ecom/crm 一闪 = **P2**，见分镜 Y-P2a；Loki = Y-P2b；回归 `python3 scripts/smoke_kit_p2.py`

---

## GTM 一句（口播可用）

> Guided OBS bootstrap plus a quality cross-cut — Base install, Metrics or Langfuse as add-ons, one doc golden path with `trace_id` in Jaeger.
