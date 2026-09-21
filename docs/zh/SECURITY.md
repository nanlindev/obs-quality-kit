# 安全（SECURITY）

默认暴露面与密钥边界。公网必须先过反代。

英文版：[../en/SECURITY.md](../en/SECURITY.md)

---

## 默认绑定（Review-1 / B19）

| 规则 | 说明 |
|------|------|
| `OBS_UI_BIND=127.0.0.1` | Jaeger / Grafana / Prom / Langfuse / cAdvisor 宿主端口默认只绑 loopback |
| 禁止无脑 `0.0.0.0` | 公网 = [REVERSE_PROXY](REVERSE_PROXY.md) + 鉴权 |
| 褐地 adopt | 若旧栈已是 `0.0.0.0`，smoke 需显式 `OBS_ALLOW_PUBLIC_UI=1` 才放行（lab 逃生口） |

检查：`docker ps` 端口列应为 `127.0.0.1:16686->…` 等形式，而非裸 `0.0.0.0`。

---

## 密钥

- **禁止**把真密码、Langfuse salt、API key 提交进 git  
- 生成物在 `.obs-kit/`（gitignore）：Grafana 密码文件、Langfuse secrets JSON、渲染 compose  
- 见 [CREDENTIALS](CREDENTIALS.md)

---

## Docker socket（metrics）

cAdvisor 只读挂载 docker.sock → 枚举容器指标。风险与缓解见 [METRICS](METRICS.md)。脚本不会自动收紧 socket。

---

## 质量闸门

`OBS_QUALITY_GATE_MODE` 默认 **shadow**（不挡业务写出）。`block` 须显式开启。见 [CONTRACT](CONTRACT.md)。

---

## Review-7 勾选

- [x] 支持矩阵仅 Compose（[INSTALL](INSTALL.md)）
- [x] UI 默认不公网裸奔
- [x] 密钥不进仓库；手册写明存放位置
