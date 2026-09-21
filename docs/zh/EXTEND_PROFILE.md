# 如何新增工程 Profile

扩展 **L1 OBS 后端组合**（例：未来 Loki），不改动 L2 契约字段语义。

英文版：[../en/EXTEND_PROFILE.md](../en/EXTEND_PROFILE.md)

## 步骤

1. 建 `profiles/<name>/`：compose 片段（若本仓自有）或编排 sibling 的说明。
2. 在 [`profiles/registry.yaml`](../../profiles/registry.yaml) 登记：`extends` / `orchestrates` / `compose_fragments` / `status`。
3. 接 bootstrap：`scripts/lib/` 编排 + `bootstrap_kit.py` 支持该 profile。
4. 预检端口/磁盘行 + `smoke_kit_bootstrap.py --profile <name>` 金路径一行。
5. 双语手册（INSTALL/METRICS 同类）+ 更新 [BASE_ADDONS](BASE_ADDONS.md) 对照表。
6. **禁止**为了新 profile 改 `contract/` 的 Scheme B / 闸门默认语义。

未登记名称 = 手册「升级/定制」，不是受支持 profile。

非 n8n 应用（Frappe / WP / 普通服务）接 L0–L2：见 [GENERIC_APP_ADAPTER](GENERIC_APP_ADAPTER.md)（指南；无实装）。

骨架说明亦见 [`profiles/README.md`](../../profiles/README.md)。安装入口：[INSTALL](INSTALL.md)。
