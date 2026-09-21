# 反代（REVERSE_PROXY）

把 OBS UI **安全**暴露到公网：反代 + TLS + 鉴权。默认宿主仍建议 `OBS_UI_BIND=127.0.0.1`，由反代进程连本机端口。

英文版：[../en/REVERSE_PROXY.md](../en/REVERSE_PROXY.md)

其它面板（Traefik 仪表盘、宝塔等）= 升级/自理；本页覆盖 **NPM / nginx / Caddy**。

---

## 通用要求

| 项 | 要求 |
|----|------|
| 后端 | `http://127.0.0.1:<OBS_*_PORT>`（勿直接把容器改成 `0.0.0.0` 省事） |
| TLS | 有效证书（Let’s Encrypt 等） |
| 鉴权 | 基本认证、SSO 或产品自带登录（Grafana/Langfuse）**至少一种** |
| WebSocket | Grafana Live 等如需要则升级 Upgrade 头 |

默认端口提醒：Jaeger `16686`、Grafana `3001`、Prometheus `9090`、Langfuse `3000`、cAdvisor `8088`。

---

## Nginx Proxy Manager（NPM）

1. Proxy Host → Domain `grafana.example.com`  
2. Forward → `http://127.0.0.1:3001`（Docker 网关场景可用 `host.docker.internal` 若 NPM 在容器内）  
3. SSL → Request certificate；Force SSL  
4. Access List 或 NPM 基本认证；Grafana 仍保留强管理员密码  
5. 同类为 Jaeger / Langfuse 各建一条（**不要**把 Prom 无鉴权裸放公网）

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

Jaeger / Langfuse：复制 server 块改 `server_name` 与 `proxy_pass` 端口即可。

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

Caddy 自动 HTTPS（公网 DNS 正确时）。

---

## 不要做的事

- 为了「好连」把 `.env` 改成 `OBS_UI_BIND=0.0.0.0` 且无反代  
- 公网暴露 Prometheus / cAdvisor 无认证  
- 把反代指到 Docker 桥 IP 却忘记防火墙  

安全总览：[SECURITY](SECURITY.md)。
