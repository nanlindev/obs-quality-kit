# Image pins (IMAGE_PIN)

This repo and orchestrated sibling OBS stacks must **not** use unpinned `latest`, untagged images, or **major-only** floating tags (e.g. `langfuse:3`, `redis:7`).

## Rules

| Rule | Detail |
|------|--------|
| Immutable tag or digest | e.g. `busybox:1.36.1`, `jaegertracing/jaeger:2.19.0`, `…@sha256:…` |
| No silent upgrades | Bootstrap/scripts must not rewrite pins to `latest` |
| Upgrade path | Change pin → re-run smoke → Maintenance Addon (PRD §6.2 / BASE_ADDONS) |
| Audit | Image refs in `docker compose config` / rendered files must be reviewable (B20) |

## Pins in this repo

| Component | Image pin | Notes |
|-----------|-----------|-------|
| `kit_scaffold` | `busybox:1.36.1` | `--profile scaffold` only |
| Prometheus | `prom/prometheus:v2.54.1` | profile `metrics` |
| Grafana | `grafana/grafana:11.2.2` | profile `metrics` |
| cAdvisor | `gcr.io/cadvisor/cadvisor:v0.49.1` | profile `metrics`; socket risk → METRICS.md |
| Loki | `grafana/loki:2.9.4` | profile `loki` |
| Promtail | `grafana/promtail:2.9.4` | profile `loki`; socket risk → LOKI.md |

## Sibling Langfuse (P2-1)

Kit render `.obs-kit/rendered/langfuse-stack.yml` (and sibling source compose) pins:

| Component | Pin |
|-----------|-----|
| langfuse-web / worker | `docker.io/langfuse/langfuse:3.225.5` / `…-worker:3.225.5` |
| ClickHouse | `docker.io/clickhouse/clickhouse-server:24.8` |
| MinIO | `cgr.dev/chainguard/minio@sha256:29bbe439d3a3…` (digest) |
| Redis | `docker.io/redis:7.4.2` |
| Postgres | `docker.io/postgres:17.5` |

**Do not** use floating `langfuse*:3` / `*:3.225` majors — Hub briefly pointed `:3` at v4. Upgrades = edit the table + `smoke --profile langfuse|full`.

otel / Jaeger pins remain in their repos; kit only rewrites publish binds.

中文版：[../zh/IMAGE_PIN.md](../zh/IMAGE_PIN.md)
