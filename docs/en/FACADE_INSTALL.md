# OBS Kit Facade — install (Stage 5)

Thin n8n facade: Scheme B IDs + one health probe. **Not** the doc golden path; no business writes.

中文版：[../zh/FACADE_INSTALL.md](../zh/FACADE_INSTALL.md)

## Prerequisites

- Shared `platform-n8n` running
- Optional: `doc-workflow` sidecar healthy (default probe `http://doc_python_ai:8001/health`)
- Or set n8n env `OBS_FACADE_HEALTH_URL` to any `/health`

## Import into platform-n8n

1. Open n8n UI (typically http://localhost:5678)
2. **Workflows → Import from File**
3. Select [`workflows/OBS Kit Facade.json`](../../workflows/OBS%20Kit%20Facade.json)
4. Activate the workflow (required for the Webhook entry)

Suggested tag: `obs-quality-kit`

## Credential rebind

This facade **needs no** Slack / Sheets / DB credentials.  
If you add third-party nodes later: re-bind credentials after import; re-link Error Workflow IDs manually if used.

## Minimal path

| Entry | Action | Expect |
|-------|--------|--------|
| Manual | Open workflow → **Test workflow** / Execute | Final item has `correlation_id`, `trace_id`, `health` |
| Webhook | `POST /webhook/obs-kit-facade` (or Test URL) | JSON with Scheme B fields + health |

Optional body: `{"correlation_id":"<uuid>"}` to pass through a business ID.

Displayed `gate_mode` defaults to **shadow** (does not block writes).

## Review-5

- Few nodes: Trigger → Build IDs → GET Health → Format → Done
- `GET Health` error output is wired to `Format Health Error` (no dangling port)
- Does not Execute Doc Process / Post (not a god-workflow)

## Static check (no n8n required)

```bash
python3 scripts/smoke_kit_facade.py
```
