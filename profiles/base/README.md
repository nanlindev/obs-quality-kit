# Profile: base

Base engineering profile = **OTEL Collector + Jaeger** (PRD §6.1).

Stage 1 bootstrap:

```bash
./scripts/bootstrap.sh up --profile base
python3 scripts/smoke_kit_bootstrap.py --profile base
```

Orchestrates sibling stacks via `OTEL_STACK_PATH` / `JAEGER_STACK_PATH`. Kit renders host binds to `OBS_UI_BIND` and uses compose project names `obs-kit-*`.
