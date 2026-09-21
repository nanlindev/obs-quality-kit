# P2 收尾说明（P2-7）

| 项 | 值 |
|----|-----|
| 状态 | **`0.2-p2-smoke-green`**（P2-0…P2-7 验收绿；**未成片**） |
| 日期 | 2026-09-17 |
| 成片 | **仍禁止**；**成片 = P2-8**（完整版 + 短版入库） |
| 上一阶段 | [P1_CLOSE.md](P1_CLOSE.md) |
| 范围 | [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md) |

英文版：[../en/P2_CLOSE.md](../en/P2_CLOSE.md)

---

## 回归命令

```bash
# 推荐：栈已 up；一键 P1 + P2
python3 scripts/smoke_kit_p2.py

# 加快：P1 只跑静态，P2 live（ecom/crm/loki/llm）
python3 scripts/smoke_kit_p2.py --p1-static

# 仅静态（不成完整收口）
python3 scripts/smoke_kit_p2.py --static-only
```

本收口覆盖：

| 层 | 内容 |
|----|------|
| P1 不回退 | `smoke_kit_p1`（contract / facade / docs / profiles / doc B） |
| P2-2/3 | `smoke_kit_ecom_path` / `smoke_kit_crm_path` |
| P2-4 | `smoke_kit_bootstrap --profile loki` |
| P2-5 | `smoke_kit_llm_ops`（无密钥 = skip，同 D7） |
| P2-6 | 文档包（`GENERIC_APP_ADAPTER` 在 `smoke_kit_docs`） |

---

## Review-P2-7

- [x] 支持矩阵仍 Compose-only（[INSTALL](INSTALL.md)）
- [x] 安全默认 loopback（[SECURITY](SECURITY.md)）
- [x] Base/Addon 边界未漂（[BASE_ADDONS](BASE_ADDONS.md)；`full` **不含** loki）
- [x] 闸门默认 shadow；契约 Scheme B 未改
- [x] 分镜已补 ecom/crm/Loki 一闪（仍 **未拍**，待 P2-8）

---

## 已知诚实项

- doc `/health.langfuse=skipped` → LLM Ops / D7 **跳过**（未配 PK/SK）
- ≤8GB 勿长期挂 `full`，更勿 `full`+`loki` 同挂
- Frappe/WP：**仅指南**，无实装（[GENERIC_APP_ADAPTER](GENERIC_APP_ADAPTER.md)）

---

## 下一步（P2-8）

| 已交付（文档） | 仍待本机 |
|----------------|----------|
| 英文 VO、[P2_8_FILM](P2_8_FILM.md)、`assets/demo/videos/` 入库约定 | 录屏 / 剪辑 / 上传 |

按 [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) 拍摄完整版 + 短版（含 Y-P2a / Y-P2b / S-P2）；两支入库后 → `0.2-p2-complete`。**勿虚标已拍。**
