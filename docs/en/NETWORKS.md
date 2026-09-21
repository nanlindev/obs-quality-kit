# Networks and Compose project prefix

Fixed kit identity for **coexistence** with `platform-n8n` and vertical workflow repos — avoid accidental attach/scrape of the wrong stack.

## Compose project name

| Item | Value |
|------|-------|
| Root / O+J identity | `obs-quality-kit` (`.env` `COMPOSE_PROJECT_NAME`) |
| Metrics addon | **`obs-quality-kit-metrics`** (own project) |
| Loki addon | **`obs-quality-kit-loki`** (own project) |
| Label prefix | `com.obsquality.kit.*` |

Addons **must not** share one compose project, and up/down **must not** use `--remove-orphans` — a later profile would otherwise delete the earlier Grafana/Prometheus (or Loki) as orphans.

**No-conflict check (Review-0):**

| Repo / stack | Compose project `name` |
|--------------|------------------------|
| `platform-n8n` | `platform-n8n` |
| `doc-workflow` | `doc-workflow` |
| `ecom-workflow` | `ecom-workflow` |
| `crm-workflow` | `crm-workflow` |
| `otel-collector-stack` etc. | Directory default when `name` unset |
| **This kit** | **`obs-quality-kit`** |

Container names look like `obs-quality-kit-<service>-1` and do not collide with `platform-n8n-*` / `doc-workflow-*`.

## External networks

| Network | Required? | Purpose |
|---------|-----------|---------|
| `proxy_network` | Yes (install) | OTEL Collector, Jaeger, Langfuse, later kit metrics targets |
| `n8n_platform` | When L3 / facade demos need it | n8n ↔ sidecars; pure acceptance A install can omit |

Both are **pre-created** by `platform-n8n/scripts/ensure-networks.sh` and declared `external: true` in compose (see platform [DOCKER_STANDARDS](../../../platform-n8n/docker/docs/DOCKER_STANDARDS.md)). If missing: create or abort with a clear message (acceptance B6); never silently stomp a conflicting network.

## Root Compose layout

```text
obs-quality-kit/
  docker-compose.yml     # wrapper → docker/compose.yml (dup/ddown)
  docker/compose.yml     # name: obs-quality-kit + networks + later services
  profiles/              # engineering profile registry + fragments
```

中文版：[../zh/NETWORKS.md](../zh/NETWORKS.md)
