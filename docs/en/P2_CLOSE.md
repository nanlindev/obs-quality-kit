# P2 close notes (P2-7)

| | |
|--|--|
| Status | **`0.2-p2-smoke-green`** (P2-0…P2-7 accepted; **not filmed**) |
| Date | 2026-09-17 |
| Film | **Still forbidden**; **film = P2-8** (full + short cuts checked in) |
| Prior | [P1_CLOSE.md](P1_CLOSE.md) |
| Scope | [PHASE2_ADDENDUM.md](PHASE2_ADDENDUM.md) |

中文版：[../zh/P2_CLOSE.md](../zh/P2_CLOSE.md)

---

## Regression

```bash
# Prefer stacks already up; one-shot P1 + P2
python3 scripts/smoke_kit_p2.py

# Faster: P1 static + P2 live (ecom/crm/loki/llm)
python3 scripts/smoke_kit_p2.py --p1-static

# Static only (not a full P2 close)
python3 scripts/smoke_kit_p2.py --static-only
```

This close covers:

| Layer | What |
|-------|------|
| P1 no-regress | `smoke_kit_p1` (contract / facade / docs / profiles / doc B) |
| P2-2/3 | `smoke_kit_ecom_path` / `smoke_kit_crm_path` |
| P2-4 | `smoke_kit_bootstrap --profile loki` |
| P2-5 | `smoke_kit_llm_ops` (no keys = skip, same as D7) |
| P2-6 | Handbook pack (`GENERIC_APP_ADAPTER` via `smoke_kit_docs`) |

---

## Review-P2-7

- [x] Support matrix still Compose-only ([INSTALL](INSTALL.md))
- [x] Safe default loopback ([SECURITY](SECURITY.md))
- [x] Base/Addon boundaries intact ([BASE_ADDONS](BASE_ADDONS.md); `full` **excludes** loki)
- [x] Gate default shadow; Scheme B unchanged
- [x] Shot list includes ecom/crm/Loki flashes (still **unfilmed**, wait for P2-8)

---

## Honest leftovers

- doc `/health.langfuse=skipped` → LLM Ops / D7 **skip** (no PK/SK)
- Avoid long-lived `full` on ≤8GB; do not co-run `full`+`loki` long-term
- Frappe/WP: **guide only**, no implementation ([GENERIC_APP_ADAPTER](GENERIC_APP_ADAPTER.md))

---

## Next (P2-8)

| Docs ready | Still on your machine |
|------------|------------------------|
| English VO, [P2_8_FILM](P2_8_FILM.md), `assets/demo/videos/` check-in | Record / edit / upload |

Film full + short per [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) (Y-P2a / Y-P2b / S-P2); after both cuts → `0.2-p2-complete`. **Do not fake filmed.**
