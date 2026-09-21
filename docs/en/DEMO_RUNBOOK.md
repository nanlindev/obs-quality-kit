# Demo runbook (DEMO_RUNBOOK)

Hand-run “talk track” path — **not** the filmed cut. Beats: [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md).

中文版：[../zh/DEMO_RUNBOOK.md](../zh/DEMO_RUNBOOK.md)

Film job (P2-8): [P2_8_FILM.md](P2_8_FILM.md) · VO [`demo-vo-full.md`](../../assets/demo-vo-full.md) / [`demo-vo-short.md`](../../assets/demo-vo-short.md) · check-in [`assets/demo/videos/`](../../assets/demo/videos/README.md)

---

## Hard rules

| Rule | Notes |
|------|-------|
| P1 | Full smoke green closes P1 — **do not film** |
| **Film** | **= P2-8 (Phase-2 film gate)**; P2-0…P2-7 smoke-green — see [P2_CLOSE](P2_CLOSE.md) |
| Shot list | Includes Y-P2a/b, S-P2; every shot stays **unfilmed** until both cuts are checked in |
| ecom/crm/Loki flash | Shot list Y-P2a / Y-P2b |
| Recording | **Human on your machine**; docs deliver VO/checklist only — do not fake filmed |

---

## 5-minute talk path (local)

```bash
# 0) Networks
../platform-n8n/scripts/ensure-networks.sh

# 1) Base or metrics
cp -n .env.example .env
./scripts/bootstrap.sh up --profile metrics
python3 scripts/smoke_kit_bootstrap.py --profile metrics

# 2) UIs (loopback by default)
open http://127.0.0.1:3001          # Grafana uid=obs-kit-infra
open http://127.0.0.1:16686         # Jaeger — search by trace_id

# 3) Doc golden path B (when sidecar is up)
python3 scripts/smoke_kit_doc_path.py --live
# or in doc repo: python3 scripts/smoke_doc_primary.py
```

Narrate in short-cut order: bootstrap → panels/Jaeger → doc + `trace_id`.

| Checkpoint | Expect |
|------------|--------|
| Prom targets | cadvisor / prometheus UP |
| Grafana | Lines present (Mac host disks may be thin; container series OK) |
| Jaeger | Open **trace_id** from health or doc response |
| `/health` | `obs_quality_gate_mode=shadow` |
| Langfuse (D7) | Deep-check only when `/health.langfuse=configured`; **`skipped` = no keys, honest skip** (not a failure) |
| Facade (optional) | After n8n import, Manual Execute shows Scheme B + health |

---

## Relation to vertical demos

- **doc-workflow** keeps its own product film/shot list; this kit narrates the cross-cut install/trace story
- Facade does **not** replace Doc Process / Post
- ecom/crm flash = **P2** (shot Y-P2a); Loki = Y-P2b; regression `python3 scripts/smoke_kit_p2.py`

---

## GTM one-liner (VO-ready)

> Guided OBS bootstrap plus a quality cross-cut — Base install, Metrics or Langfuse as add-ons, one doc golden path with `trace_id` in Jaeger.
