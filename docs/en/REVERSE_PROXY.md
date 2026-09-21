# Reverse proxy (REVERSE_PROXY)

Expose OBS UIs **safely**: reverse proxy + TLS + auth. Keep `OBS_UI_BIND=127.0.0.1` on the host; the proxy reaches loopback ports.

中文版：[../zh/REVERSE_PROXY.md](../zh/REVERSE_PROXY.md)

Other panels (Traefik dashboard, baota, etc.) = upgrade/DIY. This page covers **NPM / nginx / Caddy**.

---

## Common requirements

| Item | Requirement |
|------|-------------|
| Upstream | `http://127.0.0.1:<OBS_*_PORT>` (do not casually republish containers on `0.0.0.0`) |
| TLS | Valid certificate (Let’s Encrypt, etc.) |
| Auth | Basic auth, SSO, or product login (Grafana/Langfuse) — **at least one** |
| WebSocket | Set Upgrade headers if Grafana Live (etc.) needs it |

Port reminder: Jaeger `16686`, Grafana `3001`, Prometheus `9090`, Langfuse `3000`, cAdvisor `8088`.

---

## Nginx Proxy Manager (NPM)

1. Proxy Host → Domain `grafana.example.com`  
2. Forward → `http://127.0.0.1:3001` (or `host.docker.internal` if NPM runs in Docker)  
3. SSL → Request certificate; Force SSL  
4. Access List or NPM basic auth; keep a strong Grafana admin password  
5. Repeat for Jaeger / Langfuse (**do not** publish Prometheus unauthenticated)

---

## nginx

```nginx
# /etc/nginx/sites-available/obs-grafana.conf
server {
    listen 443 ssl http2;
    server_name grafana.example.com;

    ssl_certificate     /etc/letsencrypt/live/grafana.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/grafana.example.com/privkey.pem;

    auth_basic           "OBS Grafana";
    auth_basic_user_file /etc/nginx/.htpasswd;  # htpasswd -c ...

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Clone the server block for Jaeger / Langfuse with different `server_name` and ports.

---

## Caddy

```caddy
grafana.example.com {
    basicauth {
        # hash with: caddy hash-password
        admin JDJhJD...
    }
    reverse_proxy 127.0.0.1:3001
}

jaeger.example.com {
    basicauth {
        admin JDJhJD...
    }
    reverse_proxy 127.0.0.1:16686
}

langfuse.example.com {
    # Langfuse has its own login; still terminate TLS here
    reverse_proxy 127.0.0.1:3000
}
```

Caddy obtains HTTPS automatically when public DNS is correct.

---

## Don’t

- Set `OBS_UI_BIND=0.0.0.0` “for convenience” without a proxy  
- Expose Prometheus / cAdvisor publicly without auth  
- Point the proxy at a Docker bridge IP and forget the firewall  

Security overview: [SECURITY](SECURITY.md).
