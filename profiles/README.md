# Profile directories

Engineering profiles are registered in [`registry.yaml`](registry.yaml).

| Path | Stage | Contents |
|------|-------|----------|
| `base/` | 1 | Docs only — O+J via sibling stacks |
| `metrics/` | 2 | Kit-owned Grafana + Prometheus + cAdvisor compose fragment |
| `langfuse/` | 3 | Docs / collector linkage notes; stack stays sibling |
| `full/` | 3 | Composition marker (metrics + langfuse; **excludes** loki) |
| `loki/` | P2 | Kit-owned Loki + Promtail (standalone; may co-run with metrics) |

## How to add a profile

See bilingual guide: [docs/en/EXTEND_PROFILE.md](../docs/en/EXTEND_PROFILE.md) · [docs/zh/EXTEND_PROFILE.md](../docs/zh/EXTEND_PROFILE.md).

Sketch:

1. Add `profiles/<name>/` with compose fragment (if kit-owned) or orchestration notes.
2. Register the profile in `registry.yaml` (`extends`, `orchestrates`, `compose_fragments`).
3. Wire preflight + a smoke golden-path row.
4. Update bilingual handbooks / Base–Addon table — **do not** change L2 contract field semantics.

Unregistered names are out of scope until handbook “upgrade/custom”.
