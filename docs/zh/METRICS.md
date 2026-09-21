# OBS Metrics（Review-2）

Profile `metrics` = 底座 O+J + **本仓** Prometheus + Grafana + cAdvisor。

## 默认 scrape 范围

| Job | 目标 | 说明 |
|-----|------|------|
| `prometheus` | `localhost:9090` | 自监控 |
| `cadvisor` | `cadvisor:8080` | **容器级** CPU/内存等 |

**不做：** 业务应用自定义 exporter、全主机无过滤 scrape、Kubernetes SD。扩目标 = 改 `profiles/metrics/prometheus.yml` 后回归 smoke。

## Docker socket 风险（仅手册声明）

cAdvisor 只读挂载 `/var/run/docker.sock`，以便枚举容器指标。

| 风险 | 缓解 |
|------|------|
| 容器逃逸面扩大 | 仅 lab/受控主机；勿对不可信租户暴露 cAdvisor UI |
| 指标含容器名/标签 | 视为运维数据；公网需反代+鉴权 |
| Desktop/OrbStack 路径差异 | OrbStack 用 **containerd snapshotter** 时，经典 Docker factory 会因缺 `image/overlayfs/layerdb/.../mount-id` 而 **刮不到容器序列**（Prometheus `cadvisor` 仍 UP，Grafana CPU/Memory 却 No data）。本仓默认改挂 `/run/docker/containerd/containerd.sock` + `moby` ns |
| 图例变成容器 ID | containerd 路径下 cAdvisor 的 `name` 常为 ID。`docker-name-map` 从 Docker API 导出 `docker_container_name_info`，看板用 `group_left(cname)` 显示 compose 容器名 |

脚本**不会**自动收紧 socket；安全边界靠本页 + `OBS_UI_BIND=127.0.0.1`。

## 端口（默认 loopback）

| 服务 | 环境变量 | 默认 |
|------|----------|------|
| Prometheus | `OBS_PROMETHEUS_PORT` | 9090 |
| Grafana | `OBS_GRAFANA_PORT` | 3001（避开 Langfuse 3000） |
| cAdvisor | `OBS_CADVISOR_PORT` | 8088 |

Grafana 密码：`.env` 中 `GRAFANA_ADMIN_PASSWORD`，空则 bootstrap 生成到 `.obs-kit/grafana_admin_password.txt`。

## 命令

```bash
./scripts/bootstrap.sh up --profile metrics
python3 scripts/smoke_kit_bootstrap.py --profile metrics
# UI: http://127.0.0.1:3001  dashboard uid=obs-kit-infra
./scripts/bootstrap.sh down --profile metrics   # 只停 metrics；不碰 Loki / O+J
```

Compose project：`obs-quality-kit-metrics`（与 Loki 分离；up 不加 `--remove-orphans`）。

英文版：[../en/METRICS.md](../en/METRICS.md)
