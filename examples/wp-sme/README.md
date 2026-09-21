# WordPress SME pilot (ordinary app attach)

Minimal **WordPress marketing site** (no n8n, no Woo) to prove an ordinary CMS can sit on the kit network and emit logs + a Scheme B–style health endpoint.

| | |
|--|--|
| UI | http://127.0.0.1:8087 |
| Health | http://127.0.0.1:8087/obs-health/ |

| Compose | [`compose.yml`](compose.yml) |
| Smoke | from kit root: `python3 scripts/smoke_kit_wp_sme.py` |

## Honest boundary

| Verified by this pilot | **Not** claimed |
|------------------------|-----------------|
| WP on `proxy_network`; loopback publish | Universal WP product plugin |
| `GET /obs-health` → `shadow` + `correlation_id` | PHP native OTLP / Jaeger spans |
| Container logs scrapable by kit Promtail → Loki (when `loki` profile up) | Elementor / Woo / LMS stacks |
| Guide path in [GENERIC_APP_ADAPTER](../../docs/zh/GENERIC_APP_ADAPTER.md) | Remote Woo webhook via n8n |

## Bring up

```bash
# 0) networks
../platform-n8n/scripts/ensure-networks.sh

# 1) Loki (log proof) — required for full smoke Loki assert
cd /path/to/obs-quality-kit
./scripts/bootstrap.sh up --profile loki

# 2) WP SME + one-shot install (Acme Local Services)
cd examples/wp-sme
docker compose -f compose.yml up -d
./install.sh

# 3) smoke
cd ../..
python3 scripts/smoke_kit_wp_sme.py
```

UI: http://127.0.0.1:8087 · Health: http://127.0.0.1:8087/obs-health/ · Admin: `admin` / `admin_local_only`

## Tear down

```bash
cd examples/wp-sme
docker compose -f compose.yml down          # keep volumes
docker compose -f compose.yml down -v       # wipe DB + files
```

中文说明见 [docs/zh/GENERIC_APP_ADAPTER.md](../../docs/zh/GENERIC_APP_ADAPTER.md)「WP SME 试点」节。
