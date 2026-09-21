# OBS Loki (P2-4)

Profile `loki` = base O+J + **kit-owned** Loki + Promtail.

**Standalone profile**: may co-run with `metrics`; **not** folded into default `full` (avoid long-lived full+loki on ≤8GB hosts).

## What you get

| Component | Role |
|-----------|------|
| Loki | Log store / query (`:3100`) |
| Promtail | Docker SD scrape of container stdout (`docker.sock`) |

Smoke prefers a Loki **HTTP push + query** probe (does not require Promtail) to prove at least one queryable log line.

## Docker socket risk (Review-P2-4)

Promtail mounts `/var/run/docker.sock` read-only to discover container logs.

| Risk | Mitigation |
|------|------------|
| Larger escape surface | Lab / controlled hosts only; do not expose Loki publicly |
| Logs may contain business plaintext | Treat as ops data; prod needs reverse proxy + auth + retention |
| Desktop path quirks | Some Mac/OrbStack logs may be incomplete; smoke still uses the push probe |

## Ports (loopback by default)

| Service | Env | Default |
|---------|-----|---------|
| Loki | `OBS_LOKI_PORT` | 3100 |

## Grafana

The `metrics` Grafana stack provisions a Loki datasource (`http://loki:3100`).  
Loki-only (no metrics) → no Explore UI — expected; co-run metrics then pick Loki in Grafana Explore.

## Disk / memory

Preflight raises disk warn for `loki`. **Do not** leave loki co-running with `full` long-term on 8GB hosts.

## Commands

```bash
./scripts/bootstrap.sh up --profile loki
python3 scripts/smoke_kit_bootstrap.py --profile loki
# API: http://127.0.0.1:3100/ready
# With metrics: up metrics then up loki (or reverse; O+J idempotent; neither deletes the other)
./scripts/bootstrap.sh down --profile loki   # Loki only; leaves metrics / O+J
```

Compose project: `obs-quality-kit-loki` (separate from metrics; up does not use `--remove-orphans`).

**Do not** change `contract/` Scheme B / gate semantics ([EXTEND_PROFILE](EXTEND_PROFILE.md)).

中文版：[../zh/LOKI.md](../zh/LOKI.md)
