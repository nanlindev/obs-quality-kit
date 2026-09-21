# OBS Quality Kit — Product Requirements

| | |
|--|--|
| Version | 0.2-p2-smoke-green |
| Repo | `obs-quality-kit` (standalone) |
| Positioning | Sellable **OBS bootstrap + quality cross-cut layer**; thick plugin / thin n8n facade — not a vertical SaaS |
| Runtime | Shared `platform-n8n`; OTEL + Jaeger base; optional Langfuse, Grafana+Prometheus |
| Docs | `docs/en/` public; `docs/zh/` internal |
| Status | **P2 implementing** ([PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md)); film still gated on P2 green |

Chinese full text: [docs/zh/PRD.md](../zh/PRD.md)

---

## 1. Goals

Portfolio / Upwork (primary) / Fiverr (Base+Addons) / LinkedIn / GitHub: ship a guided-install observability and quality layer so automation (default demo: `doc-workflow`) is **installable**, **observable** (traces / optional metrics / optional LLM), and **quality-gated** (orchestrator-agnostic contract; default shadow mode).

**MVP-1 done = Acceptance A (stack up) + Acceptance B (one doc golden path).**

Long-term: may replace ad-hoc `platform-n8n` + multi-OBS repos if it becomes generic enough. **v1 does not replace** existing vertical repos in one shot.

---

## 2. Positioning

| Is | Is not |
|----|--------|
| OBS bootstrap + profiled backends | Social command center / sentiment BI SPA |
| Quality contract + thin adapters | “Most features” n8n vertical |
| Thick plugin (scripts/compose/contract/smoke) | Heavy n8n canvas logic |
| One Gig **Base + Addons** | Mapping L / G+P / full to three Fiverr packages |
| Default demo: n8n + doc | Plug-and-play any ERP/WP in MVP |

Differentiation: rules, triage, deliverable OBS combos, deeper Langfuse/quality — not more public social connectors.

---

## 3. Non-goals (MVP-1)

- Social listening, auto public replies, sentiment dashboards  
- Loki / ELK / Sentry / Tempo **implementation** (extension slot only)  
- Frappe / WordPress / ERP **implementation** (guide placeholder only)  
- K8s / Swarm / PaaS installers  
- Custom ops web admin  
- Mid-project Fiverr 75s / public cuts before MVP-1 acceptance  
- Platform-grade work sold as ultra-cheap all-in Basic  
- Silent `latest` image upgrades; unauthenticated public OBS UIs  
- Forking bootstrap/metrics logic into crm/ecom/doc/platform  

---

## 4. Architecture (L0–L3)

```text
L0  Telemetry bus: OTEL Collector + optional Prometheus scrape config
L1  Backend profiles: Jaeger (base) / Langfuse / Grafana+Prometheus / future Loki…
L2  Quality contract: correlation_id, trace_id, gate + trail hooks (orchestrator-agnostic)
L3  Adapters: thin n8n facade, doc-workflow (MVP), later ecom/crm/Frappe/WP…
```

**Hard rules:** Acceptance A must not require n8n. Quality core must not live only in non-reusable n8n Code nodes. n8n is the default L3 demo adapter.

Repo layout: kit owns scripts/profiles/contract/facade/smoke; `platform-n8n` stays shared; OBS stacks may be orchestrated first and optionally inlined later; `doc-workflow` stays a sibling with a **thin adapter** only.

Root `docker-compose.yml` wrapper + `docker/compose.yml` per platform Docker standards. Fixed compose project prefix/labels for coexistence.

---

## 5. Engineering profiles vs commerce

**Engineering (install/verify):**

| Name | Contents |
|------|----------|
| Base (always on) | OTEL Collector + Jaeger |
| `langfuse` | Base + Langfuse |
| `metrics` | Base + Grafana + Prometheus (G+P **bundled**) |
| `full` | Base + Langfuse + G+P |

**Commerce:** single **Base** Gig + **Addons** (Metrics G+P; Langfuse install; quality/LLM **integrate one flow**; image upgrade/maintenance). Do not 1:1 map engineering profiles to Fiverr tier names. Install ≠ integrate for Langfuse.

---

## 6. Quality contract (L2)

Minimal set extracted from doc-workflow (names calibrated to live code at implement time):

- `correlation_id` (business UUID) + `trace_id` (Jaeger paste) + `traceparent` propagation  
- Gate mode: `shadow` (default) | `block` (explicit)  
- Processing trail query by correlation (and optionally trace)  
- Langfuse hooks when LLM exists  

Source of truth = kit field table + optional small lib/HTTP — **not** n8n node names alone.

---

## 7. Thin n8n facade & doc path (B)

- Facade: pretty entry canvas; minimal logic; credential rebind after import; English notes on critical nodes.  
- Doc: thin adapter in `doc-workflow`; golden path + OBS assertions (`trace_id` in Jaeger; Langfuse if enabled).  
- ecom/crm = Phase-2.

Cross-cuts when wiring facade/doc: error ports wired, Error Workflow rebind, Code modes, test/production skips, keepalive documented.

---

## 8. Observability

| Signal | Tool | MVP |
|--------|------|-----|
| Traces | OTEL → Jaeger | Required base |
| Metrics | Prometheus + Grafana | Addon; default container/cAdvisor scrape |
| LLM | Langfuse | Addon |
| Business stages | Processing trail | Via contract/doc |
| Logs backend | Loki etc. | Not MVP; L1 slot |

Metrics and traces are complementary, not substitutes.

---

## 9. Security

- OBS UIs default **not** public (`127.0.0.1` or internal network only); public = reverse proxy + auth (handbook: NPM/nginx/Caddy).  
- Strong initial Grafana/Langfuse passwords into `.env` (never commit secrets).  
- Smoke/logs must not print full secrets; `.env.example` has no real secrets.  
- Constrained scrape targets; document Docker socket risk if used.  
- OTLP default internal; host publish needs firewall notes.  
- Gates default **shadow**; `block` explicit — do not brick real ERP writes by default.  
- Customer owns retention/access for data landing in Langfuse/ClickHouse.

Security smoke: assert no unauthenticated `0.0.0.0` lab leak (or document lab-only).

---

## 10. Install / ops

- **Brownfield:** adopt existing endpoint / remap ports / abort — never silent double-bind.  
- **Partial failure:** no pull before preflight pass; cleanup commands; **idempotent** re-run.  
- **Support matrix:** Docker Compose only (Linux VPS, OrbStack/Docker Desktop-class).  
- Disk preflight; avoid long-running `full` on 8GB demo hosts.  
- **Pin images** (immutable tag or digest); **no `latest`**; upgrades = maintenance Addon.  
- Rollback: documented compose/volume; no promised cross-major one-click migrate.

Compatibility stance: **semi-automated preflight + handbooks**.

---

## 11. MVP vs Phase-2

| Module | MVP-1 | Later |
|--------|-------|-------|
| Bootstrap + O+J | Yes | Richer preflight |
| Profiles langfuse / metrics / full | Yes | — |
| G+P container dash + one board | Yes | App metrics / alert rules |
| Contract + thin facade + doc adapter | Yes | — |
| Fine smoke + bootstrap fault matrix | Yes | More negatives |
| ecom/crm adapters | — | Yes |
| Loki profile | — | Yes (doc slot first) |
| Frappe/WP impl | — | Guide + paid custom |
| Demo videos | Shot-list only (no film) | **Film after Phase-2 complete** |

Phase-2 = **Addendum**, not full PRD rewrite unless positioning changes.

**Active Addendum:** [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md) (P2-0…P2-8; **film after P2 fully green**).

---

## 12. Fine smoke (required)

Every major step ends with repeatable acceptance. Bootstrap is strictest.

**Target entrypoints:** `scripts/smoke_kit_bootstrap.py` (A by profile); doc-path smoke (B). Empty panels / missing spans = fail.

**Bootstrap matrix (must land in INSTALL/smoke):** daemon down; old Compose; permissions; disk; port conflicts; missing/conflict networks; brownfield triple choice; no pull after failed preflight; partial failure cleanup; idempotent re-run; interrupt resume; Base then Addon; metrics/langfuse/full golden paths; Jaeger probe; intentional misconfig fails loudly; security bind; pinned images.

**Doc B matrix:** health; primary path; bad/mismatch; duplicate; IDs on card/trail; Jaeger by `trace_id`; Langfuse if on; broken OBS negative; shadow gate.

---

## 13. Cross-cut acceptance checklist

- [ ] L0–L3 clear; contract not n8n-only  
- [ ] Profile registry + “how to add a profile” doc (even before Loki)  
- [ ] Base/Addon vs engineering profile table consistent  
- [ ] Scheme B IDs; Jaeger uses `trace_id`  
- [ ] Shadow default; block explicit  
- [ ] UIs not publicly naked; secrets not in git  
- [ ] Pinned images; no silent latest  
- [ ] Brownfield + idempotent bootstrap  
- [ ] Compose-only support matrix  
- [ ] Smoke matrices A+B  
- [ ] Thin doc adapter; no logic fork into four old repos  
- [ ] Thin facade; credential rebind notes  
- [ ] Bilingual docs; English critical comments  
- [ ] No real customer PII in samples  
- [ ] P1 full smoke green closes P1; videos only after Phase-2; shot list may exist unfilmed  

---

## 14. Extensibility

**New L1 backend (e.g. Loki):** `profiles/<name>/` + registry + preflight + smoke row + collector pipeline if needed; **do not** change L2 semantics. Unregistered = handbook upgrade/custom.

**Non-n8n apps:** G+P and O+J attachable; Langfuse if LLM; contract needs an adapter; facade optional. Marketing may say “attachable to your app”; MVP ships **n8n + doc only**. Generic guide (Phase-2): **[GENERIC_APP_ADAPTER.md](GENERIC_APP_ADAPTER.md)** — **no** Frappe/WP implementation; paid custom.

---

## 15. Deliverables

Bootstrap scripts; pinned compose profiles; smoke A+B; bilingual INSTALL/SECURITY/CREDENTIALS/extension/troubleshooting (symptom index); reverse-proxy handbook; facade workflow JSON; doc adapter boundary notes; DEMO_RUNBOOK + shot-list draft (**film = Phase-2 end gate**); `.env.example`.

---

## 16. Decompose order (after PRD approval only)

Each step: checkable exit. After major stages: risk review (secrets, exposure, idempotency, PRD drift, narratability).

1. Repo skeleton + pin policy + gitignore  
2. Bootstrap preflight + O+J + core bootstrap smoke rows  
3. `metrics` profile + board  
4. `langfuse` + `full`  
5. Contract doc + minimal impl  
6. Thin n8n facade  
7. Doc thin adapter + B smoke  
8. Handbooks (faults, proxy, security)  
9. Doc sync; shot-list draft (no filming)  
10. **P1 close:** full smoke green (**no filming**)  
11. **Phase-2** (separate Addendum): ecom/crm etc. → then **film** full + short cuts  

---

## 17. GTM & honesty

- Upwork + portfolio primary; Fiverr Base+Addons best-effort  
- Resume/LinkedIn: outcomes + on-demand add-ons — not component SKUs as tiers  
- Honest claims: not accounting replacement, not 100% any layout, not finished GDPR product, not cheap turnkey platform  
- Control debug cost: few profiles, A/B split, fine smoke per step  

Phase-2 scope: [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md).

---

## 18. Demo / video policy

- **No** mid-project 75s  
- **Phase-1 end:** MVP-1 A+B full smoke green — **do not film yet**  
- **Film after Phase-2** fully accepted: **full cut** (~2–3 min) + **short cut** (≤90s / ≤75s trim)  
- Shot list: [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) — marked **unfilmed / wait for P2 end**  
- Talk track: [DEMO_RUNBOOK](DEMO_RUNBOOK.md)

Primary short story: bootstrap → green panels / one Jaeger trace → doc path + `trace_id` (P2 may flash ecom/crm). Full cut adds L0–L3, security, Addons, trail/Langfuse, P2 adapters.

---

## 19. Open items (non-blocking)

- Marketing name vs repo `obs-quality-kit` (P1 keeps repo name)  
- Addon USD prices (set before film / listing; **film = after Phase-2**)  
- v1 OBS layout: **decided** — kit-owned metrics; orchestrate sibling O+J+L (documented)  
- 8GB hosts: short `full` demos only  

---

*0.2-p2-smoke-green — P2-7 regression green; film = P2-8.*
