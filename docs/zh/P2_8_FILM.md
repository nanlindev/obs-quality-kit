# P2-8 成片清单（拍摄 / 剪辑 / 入库）

| 项 | 值 |
|----|-----|
| 前置 | [P2_CLOSE](P2_CLOSE.md) — `0.2-p2-smoke-green` |
| 分镜 | [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) |
| 口播 | [`demo-vo-full.md`](../../assets/demo-vo-full.md) · [`demo-vo-short.md`](../../assets/demo-vo-short.md)（英文） |
| 本页角色 | **拍摄作业单**；**不**替代本机录屏 |

英文版：[../en/P2_8_FILM.md](../en/P2_8_FILM.md)

---

## 诚实边界

| AI / 文档已交付 | **必须本机人工** |
|-----------------|------------------|
| 分镜、英文 VO、入库路径、验收勾选 | 屏幕录制、剪辑、上声、导出 mp4 |
| smoke 绿确认可拍 | 上传 YouTube / 写外链 |

未放入两支成片文件（或稳定外链）之前：**不得**把状态升到 `0.2-p2-complete`，镜头不得标「已拍」。

---

## 录前准备（约 10–15 min）

```bash
../platform-n8n/scripts/ensure-networks.sh
cd ../obs-quality-kit
./scripts/bootstrap.sh up --profile metrics   # 或 short-lived full
# 可选：./scripts/bootstrap.sh up --profile loki
# doc / ecom / crm sidecar 按 DEMO_RUNBOOK 已起
python3 scripts/smoke_kit_p2.py --p1-static --skip-doc-primary
```

UI（默认 loopback）：Grafana `:3001` · Jaeger `:16686` · Loki `:3100` · Langfuse `:3000`（若起）。

---

## 拍摄顺序

1. **完整版 Y** — 按分镜 Y01…Y09，插入 Y-P2a / Y-P2b（Y-P2c 可选）；口播跟 `demo-vo-full.md`
2. **短版 S** — S01…S04（+ 可选 S-P2 / S05）；口播跟 `demo-vo-short.md`
3. 剪辑时核对口播 **必须句**：`trace_id`、Base+Addon、禁止「低价全家桶 / 替代会计 / 任意版式 100%」

---

## 入库约定

将导出文件放到（勿提交超大二进制到 git 时可只放外链）：

| 成片 | 建议路径或外链登记 |
|------|-------------------|
| 完整版 ~2:30–3:00 | `assets/demo/videos/obs-kit-full.mp4` 或 YouTube URL |
| 短版 ≤90s（可裁 ≤75s） | `assets/demo/videos/obs-kit-short.mp4` 或 YouTube URL |

在 [`assets/demo/videos/README.md`](../../assets/demo/videos/README.md) 填入日期与 URL。

然后（人工确认文件/链接有效后）：

1. 分镜表镜头状态 → **已拍**
2. PRD / PHASE2 / README → `0.2-p2-complete`
3. DEMO_RUNBOOK 链成片路径/外链

---

## 验收勾选（P2-8）

- [ ] 完整版一支可播放
- [ ] 短版一支可播放（≤90s；Fiverr 裁切版可选）
- [ ] 口播含 **`trace_id`**（Jaeger 不用 correlation UUID）
- [ ] 口播含 **Base + Addon**
- [ ] 未宣称低价全家桶 / 替代会计 / 任意布局 100%
- [ ] 分镜已标已拍；状态 `0.2-p2-complete`
