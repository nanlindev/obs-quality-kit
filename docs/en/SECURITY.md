# Security (SECURITY)

Default exposure and secret boundaries. Public access requires a reverse proxy first.

中文版：[../zh/SECURITY.md](../zh/SECURITY.md)

---

## Default bind (Review-1 / B19)

| Rule | Notes |
|------|-------|
| `OBS_UI_BIND=127.0.0.1` | Host ports for Jaeger / Grafana / Prom / Langfuse / cAdvisor bind loopback by default |
| No casual `0.0.0.0` | Public = [REVERSE_PROXY](REVERSE_PROXY.md) + auth |
| Brownfield adopt | If the old stack already publishes `0.0.0.0`, smoke needs `OBS_ALLOW_PUBLIC_UI=1` (lab escape hatch) |

Check: `docker ps` should show `127.0.0.1:16686->…`, not bare `0.0.0.0`.

---

## Secrets

- **Never** commit real passwords, Langfuse salts, or API keys  
- Generated files live under `.obs-kit/` (gitignored): Grafana password file, Langfuse secrets JSON, rendered compose  
- See [CREDENTIALS](CREDENTIALS.md)

---

## Docker socket (metrics)

cAdvisor mounts docker.sock read-only to enumerate container metrics. Risks: [METRICS](METRICS.md). Scripts do not auto-harden the socket.

---

## Quality gate

`OBS_QUALITY_GATE_MODE` defaults to **shadow** (does not block business writes). `block` is explicit. See [CONTRACT](CONTRACT.md).

---

## Review-7 checklist

- [x] Support matrix is Compose-only ([INSTALL](INSTALL.md))
- [x] UI not publicly bound by default
- [x] Secrets stay out of git; handbook names locations
