# Profile: full

`full` = **metrics + langfuse** on top of base.

Prefer not to leave `full` running long-term on ≤8GB hosts (Review-3).

```bash
./scripts/bootstrap.sh up --profile full
python3 scripts/smoke_kit_bootstrap.py --profile full
```
