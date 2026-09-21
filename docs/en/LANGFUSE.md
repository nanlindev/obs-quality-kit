# Langfuse / full (Review-3)

Profiles:

| Profile | Contents |
|---------|----------|
| `langfuse` | Base O+J + orchestrate sibling `langfuse-stack` |
| `full` | `metrics` + `langfuse` (portfolio demo; **do not leave on ≤8GB hosts long-term**) |

## Port remaps (avoid kit metrics collisions)

Sibling defaults Langfuse UI `3001` and MinIO API `9090` clash with Grafana / Prometheus. Kit render remaps to:

| Service | Env | Default |
|---------|-----|---------|
| Langfuse UI | `OBS_LANGFUSE_UI_PORT` | **3000** (`127.0.0.1`) |
| MinIO API | `OBS_LANGFUSE_MINIO_API_PORT` | **9092** |

Open: http://127.0.0.1:3000  

## Forced secrets (Review-3)

Weak defaults `NEXTAUTH_SECRET=mysecret` / `SALT=mysalt` are rejected. Bootstrap writes strong values to `.obs-kit/langfuse_secrets.json` (gitignored).

## Collector linkage (B15)

- `otel-collector-stack/otel-collector-config.yaml` includes `otlphttp/langfuse` → `langfuse-web:3000`
- Non-empty `AUTHORIZATION` in `otel-collector-stack/.env`

## Image pins (P2-1 / B20)

Kit render and sibling source compose are **pinned** (see [IMAGE_PIN](IMAGE_PIN.md)):

- `langfuse/langfuse:3.225.5` + matching worker (**no** floating `:3`)
- MinIO: `cgr.dev/chainguard/minio@sha256:…`
- Redis `7.4.2`, Postgres `17.5`, ClickHouse `24.8`

`smoke_kit_bootstrap.py --profile langfuse|full` **hard-fails** on unpinned / major-only tags. Upgrade = change pin → re-smoke (Maintenance Addon).

- langfuse/full: default free-disk min 4GiB / warn 10GiB
- `full` with host RAM &lt; 8GiB: preflight **WARN** (non-blocking)

## Thin LLM Ops (P2-5)

**Installing** Langfuse ≠ **wiring** scores/prompts. Conventions, score ↔ `correlation_id`/`trace_id`, honest skip: [LLM_OPS.md](LLM_OPS.md).  
Deeper sample (external): sibling `doc-workflow` `PHASE2_LANGFUSE_ADDENDUM` (not rebuilt in this stage).

```bash
python3 scripts/smoke_kit_llm_ops.py          # no keys = skip (same as D7)
```

## Commands

```bash
./scripts/bootstrap.sh up --profile langfuse
python3 scripts/smoke_kit_bootstrap.py --profile langfuse
./scripts/bootstrap.sh up --profile full
python3 scripts/smoke_kit_bootstrap.py --profile full
./scripts/bootstrap.sh down --profile full
```

中文版：[../zh/LANGFUSE.md](../zh/LANGFUSE.md)
