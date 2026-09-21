# Credentials (CREDENTIALS)

Where secrets are generated, stored, and what must never enter git.

中文版：[../zh/CREDENTIALS.md](../zh/CREDENTIALS.md)

---

## Principles

| Do | Don’t |
|----|-------|
| Copy `.env.example` → `.env` | Commit a filled `.env` |
| Use bootstrap-generated strong secrets | Keep sibling weak defaults `mysecret` / `mysalt` |
| Keep local path notes for password files | Paste secrets into PRs / issues |

---

## This repo (obs-quality-kit)

| Item | Location | Notes |
|------|----------|-------|
| Compose / ports / paths | Root `.env` | Base can run without real secrets |
| Grafana admin | `GRAFANA_ADMIN_*`; empty password → `.obs-kit/grafana_admin_password.txt` | metrics / full |
| Langfuse NEXTAUTH / SALT | bootstrap → `.obs-kit/langfuse_secrets.json` | langfuse / full |
| Rendered sibling compose | `.obs-kit/rendered/*.yml` | Port remaps; gitignored |
| Quality gate | `OBS_QUALITY_GATE_MODE=shadow` | Not a secret; production semantics |

The whole `.obs-kit/` tree must stay gitignored.

---

## Siblings / verticals (not owned by the kit)

| Item | Repo | Notes |
|------|------|-------|
| n8n encryption / basic auth | `platform-n8n/.env` | Platform-owned |
| Doc DB / LLM / Langfuse PK·SK | `doc-workflow/.env` | Vertical-owned; kit documents the contract only |
| OTEL → Langfuse Basic | `otel-collector-stack/.env` `AUTHORIZATION` | B15 wiring |

After facade import: re-bind Slack/Sheets in the n8n UI — [FACADE_INSTALL](FACADE_INSTALL.md).

---

## Rotation

1. Grafana: update `.env` → `bootstrap up --profile metrics` (or restart grafana after password change)  
2. Langfuse: update secrets JSON / sibling `.env` → `up --profile langfuse`  
3. Re-run `smoke_kit_bootstrap.py --profile …`
