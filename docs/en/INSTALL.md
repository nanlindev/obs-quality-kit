# Install (INSTALL)

Entry point for OBS Quality Kit. Topic pages hold the detail.

中文版：[../zh/INSTALL.md](../zh/INSTALL.md)

---

## Support matrix (Review-7)

| Supported | Not supported (honest) |
|-----------|------------------------|
| **Docker Compose** (Linux VPS, OrbStack / Docker Desktop–class) | Kubernetes / Nomad / bare systemd |
| Same-host siblings: `platform-n8n`, OBS stacks, `doc-workflow` | Cross-host discovery, multi-tenant SaaS control plane |
| Profiles: `base` / `metrics` / `langfuse` / `full` / `loki` | Unregistered profiles ([EXTEND_PROFILE](EXTEND_PROFILE.md) = custom) |
| UI default `127.0.0.1` | Public bind without auth ([SECURITY](SECURITY.md) / [REVERSE_PROXY](REVERSE_PROXY.md)) |

**Compose only.** Other orchestrators = upgrade/custom, outside default smoke.

---

## Prerequisites

1. Docker Engine + Compose v2  
2. Default sibling layout:

```text
lindev/
  obs-quality-kit/          ← this repo
  platform-n8n/
  otel-collector-stack/
  jaeger-stack/
  langfuse-stack/           ← langfuse/full only
  doc-workflow/             ← golden path B only
```

3. Networks: `../platform-n8n/scripts/ensure-networks.sh` (`proxy_network` required)

---

## Quick path

```bash
cp .env.example .env
./scripts/bootstrap.sh preflight --profile base
./scripts/bootstrap.sh up --profile base
python3 scripts/smoke_kit_bootstrap.py --profile base
```

| Profile | Command | Notes |
|---------|---------|-------|
| base | `up --profile base` | O+J (orchestrate siblings) |
| metrics | `up --profile metrics` | + kit-owned G+P+cAdvisor |
| langfuse | `up --profile langfuse` | + orchestrate Langfuse |
| full | `up --profile full` | metrics + langfuse (**excludes** loki); avoid long-term on ≤8GB |
| loki | `up --profile loki` | + kit Loki+Promtail; may co-run with metrics |

Brownfield: `--brownfield adopt|rebind|abort` (default `OBS_BROWNFIELD` in `.env`). Manual cases: [BOOTSTRAP_MANUAL](BOOTSTRAP_MANUAL.md).

---

## Commerce Base / Addons ↔ engineering profiles

See [BASE_ADDONS](BASE_ADDONS.md). **Do not** 1:1 map Fiverr package names to compose profiles.

---

## Next

| Goal | Doc |
|------|-----|
| Where secrets live | [CREDENTIALS](CREDENTIALS.md) |
| Exposure / security | [SECURITY](SECURITY.md) |
| Public reverse proxy | [REVERSE_PROXY](REVERSE_PROXY.md) |
| Symptom index | [TROUBLESHOOTING](TROUBLESHOOTING.md) |
| Contract / facade / doc | [CONTRACT](CONTRACT.md) · [FACADE_INSTALL](FACADE_INSTALL.md) · [DOC_ADAPTER](DOC_ADAPTER.md) |
| Demo talk / shot list | [DEMO_RUNBOOK](DEMO_RUNBOOK.md) · [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) |
| P1 close | [P1_CLOSE](P1_CLOSE.md) |
| Phase-2 | [PHASE2_ADDENDUM](PHASE2_ADDENDUM.md) |
| Networks / image pins | [NETWORKS](NETWORKS.md) · [IMAGE_PIN](IMAGE_PIN.md) |
