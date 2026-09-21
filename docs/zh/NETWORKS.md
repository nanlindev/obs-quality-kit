# 网络与 Compose 项目前缀

与 `platform-n8n` / 垂直仓 **同机共存** 时，固定本仓标识，避免误连、误刮。

## Compose 项目名

| 项 | 值 |
|----|-----|
| 根 / O+J 标识 | `obs-quality-kit`（`.env` `COMPOSE_PROJECT_NAME`） |
| Metrics addon | **`obs-quality-kit-metrics`**（独立 project） |
| Loki addon | **`obs-quality-kit-loki`**（独立 project） |
| Label 前缀 | `com.obsquality.kit.*` |

Addon **不得**与彼此共用同一 compose project，也**不得**在 up/down 时带 `--remove-orphans`——否则后起的 profile 会把先起的 Grafana/Prometheus（或 Loki）当孤儿删掉。

**不冲突对照（Review-0）：**

| 仓 / 栈 | Compose project `name` |
|---------|------------------------|
| `platform-n8n` | `platform-n8n` |
| `doc-workflow` | `doc-workflow` |
| `ecom-workflow` | `ecom-workflow` |
| `crm-workflow` | `crm-workflow` |
| `otel-collector-stack` 等 | 默认目录名（无显式 `name` 时） |
| **本仓** | **`obs-quality-kit`** |

容器名前缀形如 `obs-quality-kit-<service>-1`，不会与 `platform-n8n-*` / `doc-workflow-*` 撞车。

## 外部网络

| 网络 | 必需？ | 用途 |
|------|--------|------|
| `proxy_network` | 是（装栈） | OTEL Collector、Jaeger、Langfuse、后续 kit metrics 目标 |
| `n8n_platform` | L3 / facade 演示时 | n8n ↔ sidecar；纯 A 层装栈可不依赖 |

两者由 `platform-n8n/scripts/ensure-networks.sh` **预创建**，compose 中一律 `external: true`（见 platform [DOCKER_STANDARDS](../../../platform-n8n/docker/docs/DOCKER_STANDARDS.md)）。缺失时：创建或中止并提示（验收 B6）；禁止静默另起同名网络踩踏。

## 根目录 Compose 布局

```text
obs-quality-kit/
  docker-compose.yml     # wrapper → docker/compose.yml（dup/ddown）
  docker/compose.yml     # name: obs-quality-kit + 网络 + 后期服务
  profiles/              # 工程 profile 注册表与片段
```

英文版：[../en/NETWORKS.md](../en/NETWORKS.md)
