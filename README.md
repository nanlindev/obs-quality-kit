# OBS Quality Kit

Sellable **observability bootstrap + quality cross-cut** for automation stacks (shared `platform-n8n`, default demo vertical: `doc-workflow`).

| | |
|--|--|
| Status | **P2-7 smoke-green** — P2-8 **prep ready** (VO + film checklist); films not checked in |
| PRD | [docs/zh/PRD.md](docs/zh/PRD.md) · [docs/en/PRD.md](docs/en/PRD.md) — **0.2-p2-smoke-green** |
| Phase-2 | [docs/zh/PHASE2_ADDENDUM.md](docs/zh/PHASE2_ADDENDUM.md) · [docs/en/PHASE2_ADDENDUM.md](docs/en/PHASE2_ADDENDUM.md) |
| P1 close | [docs/zh/P1_CLOSE.md](docs/zh/P1_CLOSE.md) · [docs/en/P1_CLOSE.md](docs/en/P1_CLOSE.md) |
| P2 close | [docs/zh/P2_CLOSE.md](docs/zh/P2_CLOSE.md) · [docs/en/P2_CLOSE.md](docs/en/P2_CLOSE.md) |
| Next | **P2-8 film** (human record); prep: [P2_8_FILM](docs/zh/P2_8_FILM.md) · [VO full](assets/demo-vo-full.md) / [short](assets/demo-vo-short.md) |
| **Install** | [docs/zh/INSTALL.md](docs/zh/INSTALL.md) · [docs/en/INSTALL.md](docs/en/INSTALL.md) |
| Security / Credentials | [docs/zh/SECURITY.md](docs/zh/SECURITY.md) · [docs/zh/CREDENTIALS.md](docs/zh/CREDENTIALS.md) |
| Troubleshooting | [docs/zh/TROUBLESHOOTING.md](docs/zh/TROUBLESHOOTING.md) |
| Reverse proxy | [docs/zh/REVERSE_PROXY.md](docs/zh/REVERSE_PROXY.md) |
| Base / Addons | [docs/zh/BASE_ADDONS.md](docs/zh/BASE_ADDONS.md) |
| Demo runbook / shot list | [docs/zh/DEMO_RUNBOOK.md](docs/zh/DEMO_RUNBOOK.md) · [`assets/demo-shot-list.md`](assets/demo-shot-list.md) |
| Contract (L2) | [docs/zh/CONTRACT.md](docs/zh/CONTRACT.md) · [`contract/`](contract/) |
| Facade (n8n) | [docs/zh/FACADE_INSTALL.md](docs/zh/FACADE_INSTALL.md) · [`workflows/OBS Kit Facade.json`](workflows/OBS%20Kit%20Facade.json) |
| Doc adapter | [docs/zh/DOC_ADAPTER.md](docs/zh/DOC_ADAPTER.md) |
| Ecom / CRM adapters | [docs/zh/ECOM_ADAPTER.md](docs/zh/ECOM_ADAPTER.md) · [docs/zh/CRM_ADAPTER.md](docs/zh/CRM_ADAPTER.md) |
| Loki | [docs/zh/LOKI.md](docs/zh/LOKI.md) |
| Thin LLM Ops | [docs/zh/LLM_OPS.md](docs/zh/LLM_OPS.md) |
| Generic app guide | [docs/zh/GENERIC_APP_ADAPTER.md](docs/zh/GENERIC_APP_ADAPTER.md) |
| Extend profile | [docs/zh/EXTEND_PROFILE.md](docs/zh/EXTEND_PROFILE.md) |
| Bootstrap | [docs/zh/BOOTSTRAP_MANUAL.md](docs/zh/BOOTSTRAP_MANUAL.md) |
| Metrics / Langfuse | [docs/zh/METRICS.md](docs/zh/METRICS.md) · [docs/zh/LANGFUSE.md](docs/zh/LANGFUSE.md) |
| Profiles | [profiles/registry.yaml](profiles/registry.yaml) |

## GTM (one breath)

**Upwork / portfolio first:** guided OBS install + quality cross-cut (Scheme B IDs, shadow gate, doc golden path). **Fiverr:** Base + Addons (Metrics / Langfuse / one-flow wire-in) — not three hard-mapped profile SKUs.  
**Film:** full + short cuts **only after Phase-2** — P1 ships smoke-green only ([shot list](assets/demo-shot-list.md) is draft / **未拍**).

Honest claims: not an accounting replacement, not 100% any layout, not a cheap turnkey platform dump.

## Bootstrap

```bash
cp .env.example .env
./scripts/bootstrap.sh up --profile base
./scripts/bootstrap.sh up --profile metrics     # + G/P/cAdvisor
./scripts/bootstrap.sh up --profile langfuse    # + Langfuse (UI :3000)
./scripts/bootstrap.sh up --profile loki        # + Loki+Promtail (:3100)
./scripts/bootstrap.sh up --profile full        # metrics + langfuse (no loki)
python3 scripts/smoke_kit_bootstrap.py --profile full
python3 scripts/smoke_kit_bootstrap.py --profile loki
./scripts/bootstrap.sh down --profile full
```

Langfuse UI defaults to **http://127.0.0.1:3000** (remapped so it does not clash with Grafana :3001).

## P1 regression (A+B)

```bash
python3 scripts/smoke_kit_p1.py              # contract+facade+docs + all profiles + doc B
python3 scripts/smoke_kit_p1.py --static-only
python3 scripts/smoke_kit_p2.py              # P1 + ecom/crm/loki/llm (P2-7)
python3 scripts/smoke_kit_p2.py --p1-static  # faster P2 close path
```

Individual checks:

```bash
python3 scripts/contract_example.py
python3 scripts/smoke_kit_contract.py
python3 scripts/smoke_kit_facade.py
python3 scripts/smoke_kit_doc_path.py        # live when sidecar up
python3 scripts/smoke_kit_ecom_path.py       # P2-2 OBS subset
python3 scripts/smoke_kit_crm_path.py        # P2-3 OBS subset
python3 scripts/smoke_kit_llm_ops.py         # P2-5 score / skip like D7
python3 scripts/smoke_kit_docs.py
```

Doc thin adapter (sibling `doc-workflow`, no relocate): [docs/en/DOC_ADAPTER.md](docs/en/DOC_ADAPTER.md).  
Ecom / CRM: [docs/en/ECOM_ADAPTER.md](docs/en/ECOM_ADAPTER.md) · [docs/en/CRM_ADAPTER.md](docs/en/CRM_ADAPTER.md).

Import facade into shared n8n: [docs/en/FACADE_INSTALL.md](docs/en/FACADE_INSTALL.md).
