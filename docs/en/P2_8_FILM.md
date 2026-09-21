# P2-8 film checklist (record / edit / check-in)

| | |
|--|--|
| Prerequisite | [P2_CLOSE](P2_CLOSE.md) — `0.2-p2-smoke-green` |
| Shot list | [`assets/demo-shot-list.md`](../../assets/demo-shot-list.md) |
| VO | [`demo-vo-full.md`](../../assets/demo-vo-full.md) · [`demo-vo-short.md`](../../assets/demo-vo-short.md) (English) |
| Role of this page | **Filming job sheet** — does **not** replace local screen recording |

中文版：[../zh/P2_8_FILM.md](../zh/P2_8_FILM.md)

---

## Honest boundary

| Already delivered (docs) | **Must be done on your machine** |
|--------------------------|----------------------------------|
| Shot list, English VO, check-in paths, acceptance ticks | Screen record, edit, voice, export mp4 |
| Smoke green = ready to film | Upload to YouTube / paste public URL |

Until both cuts exist as files **or** stable URLs: **do not** bump status to `0.2-p2-complete` or mark shots **filmed**.

---

## Pre-roll (~10–15 min)

```bash
../platform-n8n/scripts/ensure-networks.sh
cd ../obs-quality-kit
./scripts/bootstrap.sh up --profile metrics   # or short-lived full
# optional: ./scripts/bootstrap.sh up --profile loki
# doc / ecom / crm sidecars per DEMO_RUNBOOK
python3 scripts/smoke_kit_p2.py --p1-static --skip-doc-primary
```

UIs (loopback default): Grafana `:3001` · Jaeger `:16686` · Loki `:3100` · Langfuse `:3000` (if up).

---

## Shoot order

1. **Full Y** — Y01…Y09 plus Y-P2a / Y-P2b (Y-P2c optional); VO from `demo-vo-full.md`
2. **Short S** — S01…S04 (+ optional S-P2 / S05); VO from `demo-vo-short.md`
3. Edit must-say lines: **`trace_id`**, **Base+Addon**, no “cheap full stack / replaces accounting / 100% any layout”

---

## Check-in convention

| Cut | Suggested path or URL registry |
|-----|--------------------------------|
| Full ~2:30–3:00 | `assets/demo/videos/obs-kit-full.mp4` or YouTube URL |
| Short ≤90s (trim ≤75s) | `assets/demo/videos/obs-kit-short.mp4` or YouTube URL |

Fill [`assets/demo/videos/README.md`](../../assets/demo/videos/README.md) with date + URL.

Then (after you confirm files/links work):

1. Shot list → **filmed / 已拍**
2. PRD / PHASE2 / README → `0.2-p2-complete`
3. DEMO_RUNBOOK links the film paths/URLs

---

## Acceptance (P2-8)

- [ ] Full cut playable
- [ ] Short cut playable (≤90s; optional ≤75s trim)
- [ ] VO includes **`trace_id`** (Jaeger ≠ correlation UUID)
- [ ] VO includes **Base + Addon**
- [ ] No cheap full-stack / accounting-replacement / 100%-layout claims
- [ ] Shot list marked filmed; status `0.2-p2-complete`
