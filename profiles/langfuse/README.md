# Profile: langfuse

Addon = base + **Langfuse** (orchestrates sibling `langfuse-stack`).

```bash
./scripts/bootstrap.sh up --profile langfuse
python3 scripts/smoke_kit_bootstrap.py --profile langfuse
```

UI default: http://127.0.0.1:3000 (remapped from sibling :3001).  
See [docs/zh/LANGFUSE.md](../../docs/zh/LANGFUSE.md).
