# Profile: metrics

Addon = base + **Grafana + Prometheus + cAdvisor** (G+P bound; kit-owned).

```bash
./scripts/bootstrap.sh up --profile metrics
python3 scripts/smoke_kit_bootstrap.py --profile metrics
```

Compose: [`compose.yml`](compose.yml) · scrape: [`prometheus.yml`](prometheus.yml) · dashboard uid `obs-kit-infra`.  
Security / scrape scope: [docs/zh/METRICS.md](../../docs/zh/METRICS.md).
