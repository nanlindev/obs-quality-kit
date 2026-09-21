# 故障手册（TROUBLESHOOTING）

**症状索引** → 原因 → 动作。先对症状，再跑命令。

英文版：[../en/TROUBLESHOOTING.md](../en/TROUBLESHOOTING.md)

---

## 症状索引

| 症状 | 跳转 |
|------|------|
| 预检失败 / Docker 起不来 | [#预检与引擎](#预检与引擎) |
| **端口占用**（4317/4318/16686/9090/3000/3001…） | [#端口占用](#端口占用) |
| **4318** 连不上 / OTLP 报错 | [#OTLP-4318](#otlp-4318) |
| Jaeger 空 / 用 correlation 搜不到 | [#Jaeger-无-span](#jaeger-无-span) |
| Grafana / Prom **空面板** / No data | [#空面板](#空面板) |
| Langfuse 打不开 / 与 Grafana 抢端口 | [#Langfuse](#langfuse) |
| `proxy_network` 缺失 | [#网络](#网络) |
| smoke 失败但容器在跑 | [#Smoke](#smoke) |
| doc `/health` 或金路径红 | [#Doc-路径-B](#doc-路径-b) |
| 半失败残留 | [#清理](#清理) |

---

## 预检与引擎

| 可能原因 | 动作 |
|----------|------|
| Docker daemon 未开 | 开 OrbStack / Desktop / `systemctl start docker` |
| Compose 过旧 | 升到 Compose v2；看预检版本行 |
| 磁盘不足 | 腾空间；langfuse/full 默认更严（见 `.env` `OBS_DISK_*`） |
| 权限（socket） | 用户加入 `docker` 组或用有权限的上下文 |

```bash
./scripts/bootstrap.sh preflight --profile base
```

---

## 端口占用

预检或 `up` 报 port in use / brownfield abort。

| 动作 | 说明 |
|------|------|
| `adopt` | 沿用已在跑的 sibling 栈，不双开 |
| `rebind` | 改 `.env` 里 `OBS_*_PORT` 为闲置口后再 `up --brownfield rebind` |
| `abort` | 默认：先停冲突进程/容器再装 |

```bash
./scripts/bootstrap.sh up --profile base --brownfield adopt
# 或
# OBS_OTEL_HTTP_PORT=14318 OBS_JAEGER_UI_PORT=26686
./scripts/bootstrap.sh up --profile base --brownfield rebind
```

常用默认：`4317`/`4318`（OTLP）、`16686`（Jaeger）、`9090`（Prom）、`3001`（Grafana）、`3000`（Langfuse）、`8088`（cAdvisor）。

---

## OTLP 4318

| 症状 | 检查 |
|------|------|
| sidecar / n8n 导出失败 | 容器能否解析 `otel-collector:4318`（须在 `proxy_network`） |
| 宿主探测 | `curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4318`（无路径也可能非 200，以 collector 日志为准） |
| NO_PROXY | `otel-collector` 必须在 sidecar / platform `NO_PROXY` 内，否则会被本机 HTTP 代理劫持 |
| 端口重绑后 | 应用仍应打 **容器名:4318**；宿主端口只给本机调试 |

```bash
docker logs "$(docker ps -qf name=otel-collector)" --tail 80
```

---

## Jaeger 无 span

| 误区 | 正解 |
|------|------|
| 用 `correlation_id`（UUID）当搜索键 | Jaeger 用 **`trace_id`**（32 位 hex） |
| 刚打完立刻搜 | 等 1–几秒 batch export；再查 |
| collector 未指向 Jaeger | 查 otel-collector 配置与 `up --profile base` 是否成功 |

金路径：`python3 scripts/smoke_kit_doc_path.py --live --skip-primary`（D6）。

---

## 空面板

Grafana「No data」或 Prom 目标全红。

| 检查 | 动作 |
|------|------|
| profile | 是否 `up --profile metrics`（或 full） |
| Prom targets | http://127.0.0.1:9090/targets → `cadvisor` / `prometheus` 应为 UP |
| 数据源 | Grafana → Connections → Prometheus → `http://prometheus:9090` |
| 看板 | uid `obs-kit-infra`；时间范围选 Last 15 minutes |
| Mac / Desktop | cAdvisor 对主机路径可能偏少；**容器指标**仍应有线。过滤器勿写死仅 Linux 主机盘 |
| 绑定 | UI 在 `127.0.0.1:3001`；不是 `0.0.0.0` 外网地址 |
| 起 Loki 后 G+P 消失 | 旧 bug：同 project + `--remove-orphans`。现已拆成 `obs-quality-kit-metrics` / `obs-quality-kit-loki`；再 `up --profile metrics` 即可 |

```bash
python3 scripts/smoke_kit_bootstrap.py --profile metrics
```

---

## Langfuse

| 症状 | 动作 |
|------|------|
| `:3001` 打不开 / 变成 Grafana | kit 把 Langfuse UI 映到 **`:3000`** |
| 弱密钥拒装 | 看 `.obs-kit/langfuse_secrets.json`；勿手填 mysecret |
| collector 无 L | sibling `AUTHORIZATION` + config 中 `otlphttp/langfuse`（[LANGFUSE](LANGFUSE.md)） |
| 磁盘 / 内存 WARN | full 在小机器上属预期；可只跑 base/metrics |

---

## 网络

```bash
../platform-n8n/scripts/ensure-networks.sh
docker network ls | grep -E 'proxy_network|n8n_platform'
```

缺失 `proxy_network` → 预检 B6 失败；**不要**手建同名内部网络踩踏。

---

## Smoke

| 脚本 | 用途 |
|------|------|
| `smoke_kit_bootstrap.py --profile …` | A 层装栈 |
| `smoke_kit_contract.py` | L2 契约（无需 Docker） |
| `smoke_kit_facade.py` | facade JSON 静态 |
| `smoke_kit_doc_path.py` | B 层 doc |
| `smoke_kit_docs.py` | 本手册包静态齐全 |

失败时读 **第一行 FAIL 原因**；故意断 endpoint 应失败且可读（B18）。

---

## Doc 路径 B

| 症状 | 动作 |
|------|------|
| `:8004/health` 挂 | `doc-workflow` compose up；DB 5435 |
| 无 `obs_quality_gate_mode` | 重建 sidecar 镜像（Stage 6 补丁） |
| 主路径 extract 失败 | DeepSeek key / 样本 PDF；先跑 `doc-workflow/scripts/smoke_doc_primary.py` |

见 [DOC_ADAPTER](DOC_ADAPTER.md)。

---

## 清理

```bash
./scripts/bootstrap.sh down --profile full
# 状态：.obs-kit/state.json ；半失败看脚本 cleanup hint
```

勿对无关 compose project 执行 `down`（项目名须为 `obs-quality-kit` 或 rebind 时的 `obs-kit-*`）。
