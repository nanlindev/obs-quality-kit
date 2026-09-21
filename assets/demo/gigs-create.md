# Fiverr + Upwork Gigs — OBS Quality Kit

**视频：** 一支 ~75s（封面=架构图）→ 先上传 YouTube 未上架/公开，再贴进两平台  
**封面静帧：** `assets/demo/architecture-obs-kit-hero.png`（或同目录 svg 导出）  
**口播：** [`demo-vo-full.md`](demo-vo-full.md)  
**商品形态（采用）：单档 Base + Addons** — 与 PRD §6.2 / `BASE_ADDONS.md` 一致。  
**不要**按 doc/ecom 那样主推 Basic / Standard / Premium 三档垂直产品线。  
平台级 OBS **不要**卖成 ~$70「全包」；**Upwork 为主**，Fiverr 尽力。  
禁止：低价全家桶 / 万能 WP 插件 / 替代会计 / 「就是 compose 装个 Jaeger」。

| 待填 | 值 |
|------|-----|
| YouTube（75s） | `https://youtu.be/dMMq3edKlUw` |
| GitHub（若已公开） | `YOUR_GITHUB_URL`（无则删掉 repo 行） |

建议顺序：**先 Upwork Project Catalog** → **再 Fiverr Gig**。

---

## 0. 怎么卖（先读）

| SKU | 买家买什么 | 定价习惯 |
|-----|------------|----------|
| **Base（唯一主档）** | O+J、bootstrap、smoke、手册、安全默认绑定 | 对标你其它 Gig 的 **Standard 价或更高**，不是探路 $50 |
| **Addon: Metrics** | G+P+cAdvisor 看板 | Upwork/Fiverr **add-on** |
| **Addon: Langfuse 安装** | L UI + 安装级接通（≠ 深接入） | add-on |
| **Addon: Loki** | 日志后端 | add-on |
| **Addon: 一流通用 wire-in** | 契约接到 **一条** 流 + `trace_id` 证明 | add-on（最贵之一） |
| **Addon: 维护/升级** | pin + smoke 回归 | add-on |

| 平台 | 档位 UI | Addon 上限 | 怎么填 |
|------|---------|------------|--------|
| **Upwork Catalog** | 关 *3 Tiers* → **1 tier = Base** | **最多 3** custom | §A.5：Metrics + wire-in + Langfuse（或 Loki） |
| **Fiverr Gig** | 也可 **只开一档 = Base**（不必三栏） | **最多 2** extras | §B：Base + Metrics + wire-in；其余私信 |

---

## A. Upwork — Project Catalog（新建）

**路径：** Profile → **Project Catalog** → **Create a catalog project**

### 1. Title（≤70）

```
Observability Kit for n8n: Traces, Metrics, Quality Gate
```

Alt:

```
n8n OBS Bootstrap: Jaeger + Quality Cross-Cut (Base+Addons)
```

### 2. Category / skills

- Category: **Web, Mobile & Software Dev** → Scripting / Automation / DevOps（后台选项贴近即可）  
- Skills: `n8n` · `Docker` · `Observability` · `OpenTelemetry` · `Prometheus` · `Grafana` · `Python`

### 3. Project description（paste）

```
I install a guided observability + quality cross-cut for automation stacks — not “docker compose up Jaeger and call it done.”

What you get (Base + optional Addons):
• Bootstrap: preflight / up / down / status with profiles (base, metrics, loki, langfuse, full)
• Base: OpenTelemetry Collector + Jaeger, safe loopback defaults, smoke checks, handbooks
• Addon Metrics: Prometheus + Grafana + cAdvisor (container infra dashboard)
• Addon Langfuse: install-level UI + wiring (install ≠ deep LLM integrate)
• Addon Loki: optional logs (e.g. WordPress SME pilot on the same network)
• Quality contract: correlation_id for audit cards, trace_id for Jaeger, shadow gate by default
• Thin adapter path for one flow (default demo: doc-workflow) — I do not rebuild your vertical product

Not included / not claimed: cheap full-stack dump, a universal WordPress plugin, replacing your accounting system, or unlimited custom alerting.

75s demo: https://youtu.be/dMMq3edKlUw
```

### 4. Project summary（Catalog · 120–1200 chars）

```
Guided OBS bootstrap for n8n-style stacks: OTEL + Jaeger as Base, Metrics/Loki/Langfuse as Addons, plus a quality cross-cut (trace_id vs correlation UUID, shadow gate). You get install scripts, smoke checks, and a clear handoff—not “compose up every OBS binary.” One-flow wire-in (e.g. doc adapter) is a separate Addon. Demo: https://youtu.be/dMMq3edKlUw
```

### 5. Pricing — **1 tier + add-ons**（Upwork 推荐）

界面文案：*Customize your project with 1 or 3 pricing tiers.*

1. 右上角 **3 Tiers → Off**（关掉），只留 **一档 = Base**。  
2. 下一页 **Choose add-ons** → 勾 **Custom add-on**，按下面逐条建（可多条 *Create custom add-on*）。

#### 5a. 唯一主档（Base）

| 字段 | 粘贴 |
|------|------|
| Custom title（≤30） | `Base: OTEL + Jaeger + smoke` |
| Custom description（≤80） | `Bootstrap O+J, preflight/smoke, safe bind, runbook. Add-ons optional.` |
| Delivery days | `7`（或 5–7） |
| Revisions | `1` |
| Project price | 对标你其它 Catalog **Standard+**（不要 <$150 装整站台） |

（你截图里那串中文超长且超 30 字——改用上面英文短标题。）

#### 5b. Custom add-ons（**最多 3 个** — 只挂主卖）

Catalog 上限 **3** 条 custom add-on。建议挂下面三个；其余写进描述「message me」，或成交后再加时单。

**1 — Metrics（最常勾）**

```
Title: Metrics Addon (G+P+cAdvisor)
Description: Prometheus + Grafana + cAdvisor infra dashboard and smoke. Not custom business alerting.
For an extra: $120
Additional days: 3
```

**2 — One-flow wire-in（利润/联调税）**

```
Title: One-flow quality wire-in
Description: Thin adapter on one agreed flow — trace_id in Jaeger, shadow on health. Not a vertical rebuild.
For an extra: $300
Additional days: 7
```

**3 — Langfuse install（或改 Loki，二选一）**

默认 Langfuse（和作品集 LLM 故事更贴）：

```
Title: Langfuse install (not deep wire-in)
Description: Langfuse UI up + collector path + install smoke. Prompt/score integrate = message me / separate order.
For an extra: $120
Additional days: 3
```

若更想推日志站台，把第 3 条换成：

```
Title: Loki Addon (logs)
Description: Kit Loki + Promtail; optional log labels for a pilot app. Not full ELK. Langfuse install = message me.
For an extra: $90
Additional days: 2
```

**不进 3 槽、描述里写一句即可：**

```
Need Loki and Langfuse both, second flow, pin upgrade, or reverse-proxy hardening? Message me before order — we’ll add scope as a custom offer.
```

*Additional Revision* 可选；别占 custom 槽位。

### 6. Video / gallery

- Upload **~75s** mp4  
- Gallery: `architecture-obs-kit-hero.png` · Grafana still · Jaeger span still（可选）  
- Description 再贴 YouTube

### 7. Requirements（每条 ≤250 · 勾选 client must answer）

**1**

```
Do you already run Docker on a lab/VPS (or local OrbStack/Desktop)? OS + RAM (~GB), or write "need host guidance".
```

**2**

```
Starting from Base — which of the 3 add-ons do you want (Metrics / one-flow wire-in / Langfuse install)? Or "Base only". Need Loki or reverse-proxy? Write it here for a custom offer.
```

**3**

```
Do you already have n8n (or another orchestrator) on the same host/network? URL or "n8n not installed yet".
```

**4**（Standard/Premium）

```
For wire-in: which one flow should we attach first (e.g. existing webhook/doc path)? Can you share a non-prod sample—no production secrets in the first message?
```

### 8. Steps you’ll take

**Step 1 — Confirm host and Addon list**

```
Align on Docker host, Base delivery, which Addons were purchased, loopback vs reverse-proxy, and out-of-scope (no full-stack dump, no universal WP plugin).
```

**Step 2 — Bootstrap Base (+ purchased Addons)**

```
Run kit bootstrap/preflight, bring up O+J and any Addon stacks (Metrics/Loki/Langfuse install), verify smoke and UI on agreed bind.
```

**Step 3 — Prove trace_id / shadow (+ wire-in Addon if bought)**

```
Show Jaeger by trace_id (not correlation UUID) and health shadow. If wire-in Addon: thin adapter on one agreed flow.
```

**Step 4 — Handoff**

```
Short runbook: profiles, down/up, credentials, how to buy/add more Addons later.
```

### 9. FAQ

**Is this just installing Jaeger with Compose?**  
No. Guided profiles, smoke, safe defaults, and a quality cross-cut (`trace_id` / `correlation_id` / shadow). Jaeger alone is not the product.

**Do you rebuild my invoice / Woo / CRM product?**  
No. Vertical demos are separate. This Gig is the shared OBS + quality station; one-flow wire-in is an Addon.

**Will Langfuse score my prompts automatically?**  
Langfuse **install** ≠ wire-in. Deep prompt/score changes are a separate integrate Addon.

**WordPress?**  
Optional Loki pilot (logs + health) on the same network — not a marketplace WP plugin.

---

## B. Fiverr — Create a new Gig

**路径：** Selling → **Create a new Gig**

> 风险：别写支付回写 / 神药 AI。话术偏 **OBS install + quality cross-cut / Base+Addons**。若拒审，缩到「n8n Docker observability bootstrap + Jaeger」再提。

### Step 1 — Overview

**Gig title**（I will… ≤80）:

```
I will set up observability for n8n with Jaeger traces and quality gates
```

Alt:

```
I will install an OBS quality kit for your automation stack (Base plus Addons)
```

**Category:** Programming & Tech → **Other** / DevOps / Automation（以后台为准；避免乱贴 AI Services 除非你主卖 LLM 接入）

**Search tags（5）:**

```
n8n
observability
opentelemetry
docker
grafana
```

### Step 2 — Pricing（**1 档 + 最多 2 extras**）

与 Upwork 同逻辑：只开 **一档 Base**，不要填 Standard/Premium。

**Package（唯一）— 标题只用字母数字空格（Fiverr 很严）**

```
Title: Base OBS OTEL and Jaeger
Description: OpenTelemetry Collector and Jaeger, preflight smoke, safe bind, handoff runbook. Extras optional. Need Loki or Langfuse? Message me.
Delivery: 5 days
Revisions: 1
Price: $200–320（你现挂 $200 也可，之后再涨）
```

**不要用：** `( )` `+` `&` `/` `"` `:` `-` 以及粘贴进来的弯引号。

**Gig extras（最多 2）— Title ≤20，仅字母数字空格，手打勿粘贴：**

```
Title: Metrics
Description: I will add Prometheus Grafana and cAdvisor dashboard with smoke checks. Not custom business alerting.
Price: $120
Days: 3
```

```
Title: One flow wire in
Description: I will wire one agreed flow with trace id in Jaeger and shadow on health. Not a vertical rebuild.
Price: $150–300
Days: 4–7
```

**若 `pack1` 仍报 illegal characters：**

1. 先改掉 Basic 标题里的 `(OTEL + Jaeger)`（这常是真凶，报错却写 Gig Extra）。  
2. **取消勾选**两个 Extra → Save → 再只勾一个，**键盘手打** `Metrics`（不要从文档粘贴）。  
3. 仍不行：关掉 Extra，先把 Gig 存成草稿/过 Scope 页，再回来加 Extra。  
4. 换 Chrome 无痕；关输入法英文模式，避免全角数字。

### Step 3 — Description

```
Anyone can compose-up Jaeger. This Gig is Base + Addons for automation stacks (n8n-style).

Order Base, then tick extras if you need them:
• Base — OTEL Collector + Jaeger, bootstrap, smoke, handbooks, safe bind
• Extra: Metrics — Prometheus + Grafana + cAdvisor
• Extra: one-flow wire-in — quality contract on one path (trace_id vs correlation_id, shadow gate)

Need Loki, Langfuse install, second flow, or reverse-proxy hardening? Message me before you order — we’ll scope a custom offer.

Not claimed: cheap full-stack dump, universal WordPress plugin, replacing accounting, or 100% any layout.

75s demo: https://youtu.be/dMMq3edKlUw
```

### Step 4 — Requirements

```
1. Docker host ready? OS + RAM, or “need guidance”.
2. Base only, or which extras (Metrics / one-flow wire-in)? Anything else (Loki/Langfuse/proxy) — write it for a custom offer.
3. Existing n8n (or other) on same network? URL or “not yet”.
4. If wire-in: which one flow? One sentence, no production secrets.
```

### Step 5 — Gallery

1. **Video:** ~75s mp4  
2. Thumbnail: `architecture-obs-kit-hero.png`  
3. Optional: Grafana / Jaeger stills  

### Step 6 — Publish

- 关联 Portfolio（若有 OBS / n8n 项目）  
- 现有 n8n Gig 描述末尾可加一行：

```
Also offering an OBS Quality Kit (Base + Metrics/Langfuse Addons). Demo: https://youtu.be/dMMq3edKlUw
```

---

## C. 两平台共用检查

- [ ] YouTube：`https://youtu.be/dMMq3edKlUw`  
- [ ] 封面/架构图在 gallery  
- [ ] **Upwork：** 1 tier Base + **最多 3** add-ons（Metrics / wire-in / Langfuse）  
- [ ] **Fiverr：** 1 package Base + **最多 2** extras（Metrics / wire-in）；其余私信  
- [ ] 未宣称万能 WP / 替代会计 / 低价全家桶  
- [ ] 口播必落点：`trace_id`、Base+Addon、非 compose 全家桶

---

## D. 发布后（可选）

1. 把 YouTube URL 写入 `assets/demo/videos/README.md`  
2. 分镜标已拍；P2-8 勾选见 `docs/zh/P2_8_FILM.md`  
3. LinkedIn / GitHub README 链同一支 75s（下一波再做也行）
