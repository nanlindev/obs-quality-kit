# 凭证与密钥（CREDENTIALS）

哪里生成、哪里放、什么不能进 git。

英文版：[../en/CREDENTIALS.md](../en/CREDENTIALS.md)

---

## 原则

| 做 | 不做 |
|----|------|
| 从 `.env.example` 复制为 `.env` | 把填好密钥的 `.env` 提交 git |
| 使用 bootstrap 生成的强密钥 | 沿用 sibling 弱默认 `mysecret` / `mysalt` |
| 本地记密码文件路径 | 把密码贴进 PR / Issue |

---

## 本仓（obs-quality-kit）

| 项 | 位置 | 说明 |
|----|------|------|
| Compose / 端口 / 路径 | 根目录 `.env` | 无真 secret 亦可跑 base |
| Grafana 管理员 | `GRAFANA_ADMIN_*`；空密码 → `.obs-kit/grafana_admin_password.txt` | metrics / full |
| Langfuse NEXTAUTH / SALT | bootstrap → `.obs-kit/langfuse_secrets.json` | langfuse / full |
| 渲染后的 sibling compose | `.obs-kit/rendered/*.yml` | 含端口重绑；gitignore |
| 质量闸门 | `OBS_QUALITY_GATE_MODE=shadow` | 非密钥，但是生产语义 |

`.obs-kit/` **整目录**应在 `.gitignore` 内。

---

## Sibling / 垂直（不由 kit 保管）

| 项 | 仓 | 说明 |
|----|-----|------|
| n8n 加密钥 / 基本认证 | `platform-n8n/.env` | 平台自有 |
| Doc DB / LLM / Langfuse PK·SK | `doc-workflow/.env` | 垂直自有；kit 只文档约定 |
| OTEL → Langfuse Basic | `otel-collector-stack/.env` `AUTHORIZATION` | B15 衔接 |

Facade 导入后：Slack/Sheets 等在 n8n UI **重绑**，见 [FACADE_INSTALL](FACADE_INSTALL.md)。

---

## 轮换建议

1. 改 Grafana：更新 `.env` → `bootstrap up --profile metrics`（或改密后重启 grafana 容器）  
2. 改 Langfuse：更新 secrets JSON / sibling `.env` → 再 `up --profile langfuse`  
3. 轮换后跑对应 `smoke_kit_bootstrap.py --profile …`
