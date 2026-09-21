# Loki profile (P2-4)

Kit-owned **Loki + Promtail**. Engineering profile `loki` extends base (O+J).  
May co-run with `metrics`. **Not** part of default `full` (avoid long-lived full+loki on ≤8GB).

See [docs/zh/LOKI.md](../../docs/zh/LOKI.md) · [docs/en/LOKI.md](../../docs/en/LOKI.md).

```bash
./scripts/bootstrap.sh up --profile loki
python3 scripts/smoke_kit_bootstrap.py --profile loki
./scripts/bootstrap.sh down --profile loki
```
