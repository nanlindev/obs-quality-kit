#!/usr/bin/env python3
"""Static checks for OBS Kit Facade workflow JSON (Stage 5 / Review-5).

Does not require a running n8n. Exit 0 = pass.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / "workflows" / "OBS Kit Facade.json"


class Fail(Exception):
    pass


def _ok(msg: str) -> None:
    print(f"OK  {msg}")


def main() -> int:
    try:
        if not WF.is_file():
            raise Fail(f"missing workflow: {WF}")
        data = json.loads(WF.read_text(encoding="utf-8"))
        name = data.get("name")
        if name != "OBS Kit Facade":
            raise Fail(f"unexpected name: {name!r}")
        _ok(f"workflow name={name}")

        nodes = {n["name"]: n for n in data.get("nodes") or []}
        required = [
            "Manual Run",
            "Webhook Entry",
            "Build Scheme B IDs",
            "GET Health",
            "Format Success",
            "Format Health Error",
            "Facade Done",
        ]
        for req in required:
            if req not in nodes:
                raise Fail(f"missing node: {req}")
        _ok(f"nodes present ({len(required)} required)")

        if len(nodes) > 12:
            raise Fail(f"too many nodes ({len(nodes)}) — facade must stay thin")
        _ok(f"node count={len(nodes)} (thin)")

        # English notes on key nodes
        for key in ("Manual Run", "Build Scheme B IDs", "GET Health"):
            notes = (nodes[key].get("notes") or "").strip()
            if len(notes) < 10:
                raise Fail(f"node {key!r} needs an English notes comment")
        _ok("key nodes have English notes")

        conns = data.get("connections") or {}
        # Manual + Webhook → Build IDs
        for src in ("Manual Run", "Webhook Entry"):
            mains = (conns.get(src) or {}).get("main") or []
            targets = [l["node"] for branch in mains for l in (branch or [])]
            if "Build Scheme B IDs" not in targets:
                raise Fail(f"{src} must connect to Build Scheme B IDs")
        _ok("both triggers feed Build Scheme B IDs")

        health = nodes["GET Health"]
        if health.get("onError") != "continueErrorOutput":
            raise Fail("GET Health must use continueErrorOutput")
        health_main = (conns.get("GET Health") or {}).get("main") or []
        if len(health_main) < 2:
            raise Fail("GET Health must have success + error outputs wired")
        success_t = [l["node"] for l in (health_main[0] or [])]
        error_t = [l["node"] for l in (health_main[1] or [])]
        if "Format Success" not in success_t:
            raise Fail("GET Health success must → Format Success")
        if "Format Health Error" not in error_t:
            raise Fail("GET Health error must → Format Health Error (no dangling port)")
        _ok("GET Health error output wired (Review-5)")

        # No Slack / Sheets / god Execute Workflow to Doc *
        forbidden_types = {
            "n8n-nodes-base.slack",
            "n8n-nodes-base.googleSheets",
            "n8n-nodes-base.executeWorkflow",
        }
        for n in nodes.values():
            if n.get("type") in forbidden_types:
                raise Fail(f"forbidden heavy node type in facade: {n['type']} ({n['name']})")
        _ok("no Slack/Sheets/ExecuteWorkflow (not a god-workflow)")

        # Code mentions Scheme B fields
        js = nodes["Build Scheme B IDs"]["parameters"].get("jsCode") or ""
        for token in ("correlation_id", "trace_id", "traceparent", "shadow"):
            if token not in js:
                raise Fail(f"Build Scheme B IDs code missing {token!r}")
        _ok("Scheme B + shadow gate present in Code node")

        print("OK  smoke_kit_facade passed")
        return 0
    except Fail as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL  invalid JSON: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
