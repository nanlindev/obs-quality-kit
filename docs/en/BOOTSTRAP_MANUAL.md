# Bootstrap manual checklist (Stage 1)

Automated coverage: `scripts/smoke_kit_bootstrap.py --profile base`. Rows below are unstable or destructive — **not** in default smoke.

| # | Scenario | How to test | Expect |
|---|----------|-------------|--------|
| B3* | Docker socket permission denied | Run `./scripts/bootstrap.sh preflight` as a user without docker access | Preflight FAIL, readable |
| B5* | Port 4318 occupied then `up --brownfield abort` | `nc -l 4318` or a conflicting container | Abort; hints adopt/rebind |
| B8* | Brownfield Jaeger already up | Start `jaeger-stack` manually, then `up --brownfield adopt` | No double-start; adopt OK |
| B8* | Rebind ports | Set free `OBS_*_PORT` in `.env`, `--brownfield rebind` | New `obs-kit-*` projects start |
| B9* | Failed preflight must not pull | Stop Docker daemon, run `up` | No pull; B1 FAIL |
| B10* | Kill during bring-up | Ctrl+C during `up`, then `./scripts/bootstrap.sh down` | Cleanup hint works; down OK |
| B12* | Resume after interrupt | Same as B10*, then `up` again | Recover or clean then succeed |
| B17* | Real span | Emit OTLP from a sidecar/platform; search Jaeger by `trace_id` | Span visible (golden path Stage 6) |
| B19* | Public UI bind | Check `docker ps` for `0.0.0.0:16686` / Grafana | Kit fresh bind is `127.0.0.1`; adopted public UI needs `OBS_ALLOW_PUBLIC_UI=1` for smoke |
| B14* | metrics golden path | `smoke --profile metrics`; or open Grafana dashboard `obs-kit-infra` | Prom targets up; panels wired. Socket risk → [METRICS.md](METRICS.md) |

## Commands

```bash
cp .env.example .env
./scripts/bootstrap.sh preflight --profile base
./scripts/bootstrap.sh up --profile base
./scripts/bootstrap.sh up --profile base --brownfield adopt
./scripts/bootstrap.sh status --profile base
./scripts/bootstrap.sh down --profile base
python3 scripts/smoke_kit_bootstrap.py --profile base
```

Partial-failure cleanup: follow the script cleanup hint; state lives in `.obs-kit/state.json` (gitignored).

中文版：[../zh/BOOTSTRAP_MANUAL.md](../zh/BOOTSTRAP_MANUAL.md)
