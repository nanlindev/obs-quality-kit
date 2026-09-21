# OBS Loki（P2-4）

Profile `loki` = 底座 O+J + **本仓** Loki + Promtail。

**独立 profile**：可与 `metrics` 同开；**不**默认塞进 `full`（≤8GB 勿与 full 长期同挂）。

## 默认能力

| 组件 | 作用 |
|------|------|
| Loki | 日志存储 / 查询（`:3100`） |
| Promtail | Docker SD 刮容器 stdout（挂 `docker.sock`） |

Smoke 探针优先走 Loki **HTTP push + query**（不依赖 Promtail），证明「至少一条可查日志」。

## Docker socket 风险（Review-P2-4）

Promtail 只读挂载 `/var/run/docker.sock` 以发现容器日志。

| 风险 | 缓解 |
|------|------|
| 容器逃逸面扩大 | 仅 lab/受控主机；勿公网裸奔 Loki |
| 日志含业务明文 | 视为运维数据；生产需反代+鉴权+留存策略 |
| Desktop 路径差异 | Mac/OrbStack 上部分容器日志可能不全；smoke 仍以 push 探针为准 |

## 端口（默认 loopback）

| 服务 | 环境变量 | 默认 |
|------|----------|------|
| Loki | `OBS_LOKI_PORT` | 3100 |

## 与 Grafana

`metrics` 的 Grafana 已预置 Loki datasource（`http://loki:3100`）。  
仅起 Loki、未起 metrics 时 Explore 不可用——属预期；同开后在 Grafana Explore 选 Loki。

## 磁盘 / 内存

预检对 `loki` 提高磁盘 warn；手册：**勿与 `full` 在 8GB 机长期同挂**。

## 命令

```bash
./scripts/bootstrap.sh up --profile loki
python3 scripts/smoke_kit_bootstrap.py --profile loki
# API: http://127.0.0.1:3100/ready
# 与 metrics 同开：先 up metrics，再 up loki（或反过来；O+J 幂等；互不删除）
./scripts/bootstrap.sh down --profile loki   # 只停 Loki；不碰 metrics / O+J
```

Compose project：`obs-quality-kit-loki`（与 metrics 分离；up 不加 `--remove-orphans`）。

**不改** `contract/` Scheme B / 闸门语义（[EXTEND_PROFILE](EXTEND_PROFILE.md)）。

英文版：[../en/LOKI.md](../en/LOKI.md)
