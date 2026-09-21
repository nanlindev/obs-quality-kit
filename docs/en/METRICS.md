# OBS Metrics (Review-2)

Profile `metrics` = base O+J + **kit-owned** Prometheus + Grafana + cAdvisor.

## Default scrape scope

| Job | Target | Notes |
|-----|--------|-------|
| `prometheus` | `localhost:9090` | Self-scrape |
| `cadvisor` | `cadvisor:8080` | **Container-level** CPU/memory |

**Out of scope:** app exporters, unfiltered host scrape, Kubernetes SD. Extend via `profiles/metrics/prometheus.yml` + re-run smoke.

## Docker socket risk (handbook-only)

cAdvisor mounts `/var/run/docker.sock` read-only to enumerate containers.

| Risk | Mitigation |
|------|------------|
| Larger escape surface | Lab/controlled hosts only; do not expose cAdvisor UI publicly |
| Metrics include names/labels | Treat as ops data; public = reverse proxy + auth |
| Desktop/OrbStack paths | OrbStack **containerd snapshotter** breaks classic Docker factory (`image/overlayfs/layerdb/.../mount-id` missing) → Prom `cadvisor` UP but Grafana CPU/Memory **No data**. Default mounts `/run/docker/containerd/containerd.sock` + `moby` ns |
| Legends show container IDs | Under containerd, cAdvisor `name` is often the ID. `docker-name-map` exports `docker_container_name_info` from the Docker API; the dashboard joins with `group_left(cname)` for compose-friendly legends |

Scripts do **not** auto-harden the socket; rely on this page + `OBS_UI_BIND=127.0.0.1`.

## Ports (loopback by default)

| Service | Env | Default |
|---------|-----|---------|
| Prometheus | `OBS_PROMETHEUS_PORT` | 9090 |
| Grafana | `OBS_GRAFANA_PORT` | 3001 (avoid Langfuse 3000) |
| cAdvisor | `OBS_CADVISOR_PORT` | 8088 |

Grafana password: `GRAFANA_ADMIN_PASSWORD` in `.env`, or generated under `.obs-kit/grafana_admin_password.txt`.

## Commands

```bash
./scripts/bootstrap.sh up --profile metrics
python3 scripts/smoke_kit_bootstrap.py --profile metrics
# UI: http://127.0.0.1:3001  dashboard uid=obs-kit-infra
./scripts/bootstrap.sh down --profile metrics   # metrics only; leaves Loki / O+J
```

Compose project: `obs-quality-kit-metrics` (separate from Loki; up does not use `--remove-orphans`).

中文版：[../zh/METRICS.md](../zh/METRICS.md)
