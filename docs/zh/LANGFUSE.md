# Langfuse / full（Review-3）

Profile：

| Profile | 组成 |
|---------|------|
| `langfuse` | 底座 O+J + 编排 sibling `langfuse-stack` |
| `full` | `metrics` + `langfuse`（作品集全家桶；**勿在 ≤8GB 机长期挂**） |

## 端口重绑（避免与 kit metrics 互抢）

Sibling 默认 Langfuse UI `3001`、MinIO API `9090` 会撞 Grafana / Prometheus。kit 渲染时改为：

| 服务 | 环境变量 | 默认 |
|------|----------|------|
| Langfuse UI | `OBS_LANGFUSE_UI_PORT` | **3000**（`127.0.0.1`） |
| MinIO API | `OBS_LANGFUSE_MINIO_API_PORT` | **9092** |

打开：http://127.0.0.1:3000  

## 密钥强制（Review-3）

弱默认 `NEXTAUTH_SECRET=mysecret` / `SALT=mysalt` **禁止沿用**。bootstrap 生成强密钥写入 `.obs-kit/langfuse_secrets.json`（gitignore）。

## Collector 衔接（B15）

- `otel-collector-stack/otel-collector-config.yaml` 含 `otlphttp/langfuse` → `langfuse-web:3000`
- `otel-collector-stack/.env` 中 `AUTHORIZATION`（Basic）非空

## 镜像钉扎（P2-1 / B20）

kit 渲染与 sibling 源 compose **已钉扎**（见 [IMAGE_PIN](IMAGE_PIN.md)）：

- `langfuse/langfuse:3.225.5` + worker 同版本（**禁止**浮动 `:3`）
- MinIO：`cgr.dev/chainguard/minio@sha256:…`
- Redis `7.4.2`、Postgres `17.5`、ClickHouse `24.8`

`smoke_kit_bootstrap.py --profile langfuse|full` 对未钉扎 / major-only tag **硬失败**。升级 = 改 pin → 回归 smoke（维护 Addon）。

- langfuse/full：空闲磁盘默认 min 4GiB / warn 10GiB
- `full` 且主机 RAM &lt; 8GiB：预检 **WARN**（不硬拦）

## 薄 LLM Ops（P2-5）

**安装** Langfuse ≠ **接入** score/prompt。接入约定、score ↔ `correlation_id`/`trace_id`、诚实 skip：见 [LLM_OPS.md](LLM_OPS.md)。  
更深样板外链：sibling `doc-workflow` 的 `PHASE2_LANGFUSE_ADDENDUM`（本 Stage 不重做 Dataset/Prompt 平台）。

```bash
python3 scripts/smoke_kit_llm_ops.py          # 无密钥 = skip（同 D7）
```

## 命令

```bash
./scripts/bootstrap.sh up --profile langfuse
python3 scripts/smoke_kit_bootstrap.py --profile langfuse   # B15 + B18 子集
./scripts/bootstrap.sh up --profile full
python3 scripts/smoke_kit_bootstrap.py --profile full       # B14+B15+B16
./scripts/bootstrap.sh down --profile full
```

英文版：[../en/LANGFUSE.md](../en/LANGFUSE.md)
