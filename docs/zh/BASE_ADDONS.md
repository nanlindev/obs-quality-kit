# Base / Addons ↔ 工程 Profile

商业话术（Gig）与 compose **工程 profile** 对照。二者相关但 **不是** 同名同义。

英文版：[../en/BASE_ADDONS.md](../en/BASE_ADDONS.md)

---

## 对照表

| 商业（PRD） | 工程 profile / 交付 | 不含 |
|-------------|---------------------|------|
| **Base** | `base`：O+J、bootstrap、手册、smoke A、默认安全绑定 | 不改客户业务代码；不默认 G+P / L |
| **Addon: Metrics (G+P)** | `metrics`：kit Grafana+Prom+cAdvisor + [METRICS](METRICS.md) | 业务自定义告警大全 |
| **Addon: Langfuse 安装** | `langfuse`：L UI + collector 可接 + smoke B15 | 完整 LLM Ops / 改 sidecar 深接入 |
| **Addon: Loki（日志）** | `loki`：kit Loki+Promtail + [LOKI](LOKI.md)；可与 metrics 同开 | ELK 全家桶；勿与 full 长期同挂 |
| **Addon: 质检或 LLM 接入（1 流）** | 契约 + MVP=`doc` 金路径（[DOC_ADAPTER](DOC_ADAPTER.md)） | 无限改需求；第二条流另计 |
| **Addon: 维护/升级** | 改镜像 pin、回归 smoke | 自动 `latest` |
| 作品集全家桶（非单独 SKU） | `full` = metrics + langfuse（**不含** loki） | ≤8GB 勿长期挂 |

Fiverr「三档套餐」**不要**硬映射成 `base|metrics|full` 三个 profile 名。

---

## 安装 Addon vs 接入 Addon

| 类型 | 含义 | 脚本能否一次做完 |
|------|------|------------------|
| **安装** | 栈起来、UI/ingest 通、smoke 绿 | 能（bootstrap + smoke） |
| **接入** | 改 sidecar prompt/score/闸门行为 | **不能**自动；属深度交付 |

薄 LLM Ops（score ↔ Scheme B、诚实 skip）：[LLM_OPS.md](LLM_OPS.md)。

---

## 扩展

新增 L1 后端：[EXTEND_PROFILE](EXTEND_PROFILE.md)。`loki` 已登记（P2-4）。未登记名称 = 升级/定制，不是受支持 profile。
