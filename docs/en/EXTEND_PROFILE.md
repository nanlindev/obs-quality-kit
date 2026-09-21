# How to add an engineering profile

Extend **L1 OBS backend combos** (e.g. future Loki) without changing L2 contract field semantics.

中文版：[../zh/EXTEND_PROFILE.md](../zh/EXTEND_PROFILE.md)

## Steps

1. Create `profiles/<name>/`: compose fragment (if kit-owned) or sibling orchestration notes.
2. Register in [`profiles/registry.yaml`](../../profiles/registry.yaml): `extends` / `orchestrates` / `compose_fragments` / `status`.
3. Wire bootstrap: `scripts/lib/` + `bootstrap_kit.py` support for the profile.
4. Preflight ports/disk row + `smoke_kit_bootstrap.py --profile <name>` golden path.
5. Bilingual handbook (INSTALL/METRICS-style) + update [BASE_ADDONS](BASE_ADDONS.md).
6. **Do not** change `contract/` Scheme B / default gate semantics for a new profile.

Unregistered names = handbook “upgrade/custom”, not a supported profile.

Non-n8n apps (Frappe / WP / generic services) attaching L0–L2: [GENERIC_APP_ADAPTER](GENERIC_APP_ADAPTER.md) (guide only; no implementation).

See also [`profiles/README.md`](../../profiles/README.md). Install entry: [INSTALL](INSTALL.md).
