# Bootstrap 手测清单（Stage 1）

自动化覆盖见 `scripts/smoke_kit_bootstrap.py --profile base`。下列项不稳定或破坏性大，**不进默认 smoke**。

| # | 场景 | 怎么测 | 期望 |
|---|------|--------|------|
| B3* | Docker socket 权限不足 | 用无 docker 组用户跑 `./scripts/bootstrap.sh preflight` | 预检 FAIL，可读 |
| B5* | 故意占用 4318 后再 `up --brownfield abort` | `nc -l 4318` 或起冲突容器 | abort，提示 adopt/rebind |
| B8* | 褐地已有 Jaeger UI | 先手起 `jaeger-stack`，再 `up --brownfield adopt` | 不双开；adopt 成功 |
| B8* | 换端口另起 | 改 `.env` 中 `OBS_*_PORT` 为闲置口，`--brownfield rebind` | 新项目名 `obs-kit-*` 起来 |
| B9* | 预检失败不拉镜像 | 停 daemon 后 `up` | 无 pull；B1 FAIL |
| B10* | 拉起中杀进程 | `up` 中 Ctrl+C，再 `./scripts/bootstrap.sh down` | 清理提示可用；可 down |
| B12* | 中断后再跑 | 同上后再次 `up` | 可恢复或清理后成功 |
| B17* | 真 span | sidecar/平台打一条 OTLP，Jaeger 用 `trace_id` 查 | 有 span（金路径 Stage 6） |
| B19* | 公网裸奔 | 检查 `docker ps` 端口是否 `0.0.0.0:16686` / Grafana | kit fresh 应为 `127.0.0.1`；adopt 褐地若公网需 `OBS_ALLOW_PUBLIC_UI=1` 才过 smoke |
| B14* | metrics 金路径 | `smoke --profile metrics`；或手开 Grafana 看板 `obs-kit-infra` | Prom targets up；看板有线。socket 风险见 [METRICS.md](METRICS.md) |

## 常用命令

```bash
cp .env.example .env
./scripts/bootstrap.sh preflight --profile base
./scripts/bootstrap.sh up --profile base
./scripts/bootstrap.sh up --profile base --brownfield adopt   # 褐地
./scripts/bootstrap.sh status --profile base
./scripts/bootstrap.sh down --profile base
python3 scripts/smoke_kit_bootstrap.py --profile base
```

半失败清理：见脚本打印的 `cleanup hint`；状态在 `.obs-kit/state.json`（gitignore）。

英文版：[../en/BOOTSTRAP_MANUAL.md](../en/BOOTSTRAP_MANUAL.md)
