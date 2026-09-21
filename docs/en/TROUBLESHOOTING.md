# Troubleshooting

**Symptom index** → cause → action. Match the symptom first.

中文版：[../zh/TROUBLESHOOTING.md](../zh/TROUBLESHOOTING.md)

---

## Symptom index

| Symptom | Jump |
|---------|------|
| Preflight fail / Docker down | [#Preflight--engine](#preflight--engine) |
| **Port in use** (4317/4318/16686/9090/3000/3001…) | [#Port-conflict](#port-conflict) |
| **4318** unreachable / OTLP errors | [#OTLP-4318](#otlp-4318) |
| Empty Jaeger / searching by correlation | [#Empty-Jaeger](#empty-jaeger) |
| Grafana / Prom **empty panel** / No data | [#Empty-panel](#empty-panel) |
| Langfuse down / port clash with Grafana | [#Langfuse](#langfuse) |
| Missing `proxy_network` | [#Networks](#networks) |
| Smoke red while containers run | [#Smoke](#smoke) |
| Doc `/health` or golden path red | [#Doc-path-B](#doc-path-b) |
| Half-failed leftover | [#Cleanup](#cleanup) |

---

## Preflight & engine

| Likely cause | Action |
|--------------|--------|
| Docker daemon stopped | Start OrbStack / Desktop / `systemctl start docker` |
| Old Compose | Upgrade to Compose v2; read preflight version line |
| Disk low | Free space; langfuse/full thresholds stricter (`OBS_DISK_*`) |
| Socket permission | Add user to `docker` group or use a privileged context |

```bash
./scripts/bootstrap.sh preflight --profile base
```

---

## Port conflict

Preflight or `up` reports port in use / brownfield abort.

| Action | Notes |
|--------|-------|
| `adopt` | Reuse running sibling stacks; do not double-start |
| `rebind` | Change `OBS_*_PORT` in `.env` to free ports, then `up --brownfield rebind` |
| `abort` | Default: stop the conflicting process/container first |

```bash
./scripts/bootstrap.sh up --profile base --brownfield adopt
# or
# OBS_OTEL_HTTP_PORT=14318 OBS_JAEGER_UI_PORT=26686
./scripts/bootstrap.sh up --profile base --brownfield rebind
```

Defaults: `4317`/`4318` (OTLP), `16686` (Jaeger), `9090` (Prom), `3001` (Grafana), `3000` (Langfuse), `8088` (cAdvisor).

---

## OTLP 4318

| Symptom | Check |
|---------|-------|
| Sidecar / n8n export fails | Can the container resolve `otel-collector:4318`? (must be on `proxy_network`) |
| Host probe | `curl` against `http://127.0.0.1:4318` — status may not be 200; prefer collector logs |
| NO_PROXY | `otel-collector` must be in sidecar / platform `NO_PROXY` or a local HTTP proxy steals traffic |
| After port rebind | Apps still target **container:4318**; host publish is for local debug only |

```bash
docker logs "$(docker ps -qf name=otel-collector)" --tail 80
```

---

## Empty Jaeger

| Mistake | Fix |
|---------|-----|
| Search by `correlation_id` (UUID) | Jaeger needs **`trace_id`** (32-char hex) |
| Search immediately after emit | Wait 1–few seconds for batch export |
| Collector not wired to Jaeger | Check otel-collector config and `up --profile base` |

Golden check: `python3 scripts/smoke_kit_doc_path.py --live --skip-primary` (D6).

---

## Empty panel

Grafana “No data” or Prometheus targets all red.

| Check | Action |
|-------|--------|
| Profile | Did you `up --profile metrics` (or full)? |
| Prom targets | http://127.0.0.1:9090/targets → `cadvisor` / `prometheus` should be UP |
| Datasource | Grafana → Prometheus → `http://prometheus:9090` |
| Dashboard | uid `obs-kit-infra`; time range Last 15 minutes |
| Mac / Desktop | Host paths for cAdvisor may be thin; **container** series should still draw |
| Bind | UI is `127.0.0.1:3001`, not a public `0.0.0.0` URL |
| G+P gone after Loki up | Fixed: separate projects `obs-quality-kit-metrics` / `obs-quality-kit-loki`; re-run `up --profile metrics` |

```bash
python3 scripts/smoke_kit_bootstrap.py --profile metrics
```

---

## Langfuse

| Symptom | Action |
|---------|--------|
| `:3001` is Grafana | Kit maps Langfuse UI to **`:3000`** |
| Weak-secret refusal | Use `.obs-kit/langfuse_secrets.json`; do not keep mysecret |
| Collector missing L | Sibling `AUTHORIZATION` + `otlphttp/langfuse` ([LANGFUSE](LANGFUSE.md)) |
| Disk / RAM WARN | Expected on small hosts for full; prefer base/metrics |

---

## Networks

```bash
../platform-n8n/scripts/ensure-networks.sh
docker network ls | grep -E 'proxy_network|n8n_platform'
```

Missing `proxy_network` → preflight B6 fail; **do not** silently create a colliding internal network.

---

## Smoke

| Script | Role |
|--------|------|
| `smoke_kit_bootstrap.py --profile …` | Layer A stacks |
| `smoke_kit_contract.py` | L2 contract (no Docker) |
| `smoke_kit_facade.py` | Facade JSON static |
| `smoke_kit_doc_path.py` | Layer B doc |
| `smoke_kit_docs.py` | Handbook pack completeness |

Read the first **FAIL** line. Intentional bad endpoints must fail clearly (B18).

---

## Doc path B

| Symptom | Action |
|---------|--------|
| `:8004/health` down | Bring up `doc-workflow` compose; DB on 5435 |
| No `obs_quality_gate_mode` | Rebuild sidecar image (Stage 6 patch) |
| Extract failures | DeepSeek key / sample PDFs; run `doc-workflow/scripts/smoke_doc_primary.py` |

See [DOC_ADAPTER](DOC_ADAPTER.md).

---

## Cleanup

```bash
./scripts/bootstrap.sh down --profile full
# State: .obs-kit/state.json ; half-failure → script cleanup hint
```

Do not `down` unrelated compose projects (name must be `obs-quality-kit` or rebind `obs-kit-*`).
