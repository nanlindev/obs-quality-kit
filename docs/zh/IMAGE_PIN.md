# 镜像钉扎（IMAGE_PIN）

本仓与编排的 sibling OBS 栈 **禁止** 使用未钉扎的 `latest`、无 tag、以及 **仅 major** 的浮动 tag（如 `langfuse:3`、`redis:7`）。

## 规则

| 规则 | 说明 |
|------|------|
| 不可变 tag 或 digest | 例：`busybox:1.36.1`、`jaegertracing/jaeger:2.19.0`、`…@sha256:…` |
| 禁止静默升级 | bootstrap / 脚本不得自动把 pin 改成 `latest` |
| 升级路径 | 改 pin → 回归 smoke → 属于维护 Addon（见 PRD §6.2 / BASE_ADDONS） |
| 审计 | `docker compose config` / 渲染产物可人工核对（验收 B20） |

## 本仓引用

| 组件 | 镜像 pin | 备注 |
|------|----------|------|
| `kit_scaffold` | `busybox:1.36.1` | 仅 `--profile scaffold` |
| Prometheus | `prom/prometheus:v2.54.1` | profile `metrics` |
| Grafana | `grafana/grafana:11.2.2` | profile `metrics` |
| cAdvisor | `gcr.io/cadvisor/cadvisor:v0.49.1` | profile `metrics`；socket 风险见 METRICS.md |
| Loki | `grafana/loki:2.9.4` | profile `loki` |
| Promtail | `grafana/promtail:2.9.4` | profile `loki`；socket 风险见 LOKI.md |

## Sibling Langfuse（P2-1）

kit 渲染 `.obs-kit/rendered/langfuse-stack.yml`（及 sibling 源 compose）钉扎：

| 组件 | pin |
|------|-----|
| langfuse-web / worker | `docker.io/langfuse/langfuse:3.225.5` / `…-worker:3.225.5` |
| ClickHouse | `docker.io/clickhouse/clickhouse-server:24.8` |
| MinIO | `cgr.dev/chainguard/minio@sha256:29bbe439d3a3…`（digest） |
| Redis | `docker.io/redis:7.4.2` |
| Postgres | `docker.io/postgres:17.5` |

**勿用** `langfuse*:3` / `*:3.225` 浮动 major：Hub 曾把 `:3` 指到 v4 镜像。升级 = 改上表 pin + `smoke --profile langfuse|full`。

otel / Jaeger 的 pin 仍以各自仓为准；kit 只做端口绑定重写。

英文版：[../en/IMAGE_PIN.md](../en/IMAGE_PIN.md)
