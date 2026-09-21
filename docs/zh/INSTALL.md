# 安装（INSTALL）

OBS Quality Kit 安装入口。细项见各专题页。

英文版：[../en/INSTALL.md](../en/INSTALL.md)

---

## 支持矩阵（Review-7）

| 支持 | 不支持（诚实声明） |
|------|-------------------|
| **Docker Compose**（Linux VPS、OrbStack / Docker Desktop 同类） | Kubernetes / Nomad / systemd 裸装 |
| 同机 sibling：`platform-n8n`、OBS 三仓、`doc-workflow` | 跨机自动发现、多租户 SaaS 控制面 |
| 工程 profile：`base` / `metrics` / `langfuse` / `full` / `loki` | 未登记 profile（见 [EXTEND_PROFILE](EXTEND_PROFILE.md) = 定制） |
| UI 默认 `127.0.0.1` | 无鉴权公网裸奔（见 [SECURITY](SECURITY.md) / [REVERSE_PROXY](REVERSE_PROXY.md)） |

**仅 Compose。** 其它编排 = 升级/定制，不在默认 smoke 范围。

---

## 前置

1. Docker Engine + Compose v2  
2. 仓库布局（默认相对路径）：

```text
lindev/
  obs-quality-kit/          ← 本仓
  platform-n8n/
  otel-collector-stack/
  jaeger-stack/
  langfuse-stack/           ← langfuse/full 才需要
  doc-workflow/             ← 金路径 B 才需要
```

3. 网络：`../platform-n8n/scripts/ensure-networks.sh`（`proxy_network` 必需）

---

## 快速路径

```bash
cp .env.example .env
./scripts/bootstrap.sh preflight --profile base
./scripts/bootstrap.sh up --profile base
python3 scripts/smoke_kit_bootstrap.py --profile base
```

| Profile | 命令 | 说明 |
|---------|------|------|
| base | `up --profile base` | O+J（编排现有仓） |
| metrics | `up --profile metrics` | + kit 自有 G+P+cAdvisor |
| langfuse | `up --profile langfuse` | + 编排 Langfuse |
| full | `up --profile full` | metrics + langfuse（**不含** loki）；≤8GB 勿长期挂 |
| loki | `up --profile loki` | + kit Loki+Promtail；可与 metrics 同开 |

褐地冲突：`--brownfield adopt|rebind|abort`（默认见 `.env` `OBS_BROWNFIELD`）。手测：[BOOTSTRAP_MANUAL](BOOTSTRAP_MANUAL.md)。

---

## 商业 Base / Addon ↔ 工程 profile

见 [BASE_ADDONS](BASE_ADDONS.md)。**不要**把 Fiverr 套餐名 1:1 当成 compose profile。

---

## 下一步

| 目标 | 文档 |
|------|------|
| 密钥放哪 | [CREDENTIALS](CREDENTIALS.md) |
| 暴露面 / 安全 | [SECURITY](SECURITY.md) |
| 公网反代 | [REVERSE_PROXY](REVERSE_PROXY.md) |
| 故障症状索引 | [TROUBLESHOOTING](TROUBLESHOOTING.md) |
| 契约 / facade / doc | [CONTRACT](CONTRACT.md) · [FACADE_INSTALL](FACADE_INSTALL.md) · [DOC_ADAPTER](DOC_ADAPTER.md) |
| 演示讲法 / 分镜 | [DEMO_RUNBOOK](DEMO_RUNBOOK.md) · [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) |
| P1 收尾 | [P1_CLOSE](P1_CLOSE.md) |
| Phase-2 | [PHASE2_ADDENDUM](PHASE2_ADDENDUM.md) |
| 网络 / 镜像钉扎 | [NETWORKS](NETWORKS.md) · [IMAGE_PIN](IMAGE_PIN.md) |
