#!/usr/bin/env python3
"""Contract assertions (Stage 4) — no Docker / n8n required.

Exit 0 = pass.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contract import (  # noqa: E402
    DEFAULT_GATE_MODE,
    GateMode,
    TrailQuery,
    build_traceparent,
    ensure_correlation_id,
    is_valid_correlation_id,
    is_valid_trace_id,
    is_valid_traceparent,
    parse_gate_mode,
    resolve_ids,
    trail_query_url,
)
from contract.gate import should_block_writes  # noqa: E402


class ContractTests(unittest.TestCase):
    def test_correlation_uuid(self) -> None:
        cid = ensure_correlation_id(None)
        self.assertTrue(is_valid_correlation_id(cid))
        self.assertEqual(ensure_correlation_id(cid), cid)
        self.assertTrue(is_valid_correlation_id(ensure_correlation_id("not-a-uuid")))

    def test_resolve_ids_shape(self) -> None:
        ids = resolve_ids(headers={"X-Correlation-Id": "550e8400-e29b-41d4-a716-446655440000"})
        self.assertEqual(ids.correlation_id, "550e8400-e29b-41d4-a716-446655440000")
        self.assertTrue(is_valid_trace_id(ids.trace_id))
        self.assertTrue(is_valid_traceparent(ids.traceparent))
        self.assertIn(ids.trace_id, ids.traceparent)
        body = ids.as_dict()
        self.assertEqual(set(body), {"correlation_id", "trace_id", "traceparent"})

    def test_traceparent_roundtrip(self) -> None:
        tp = build_traceparent(trace_id="4bf92f3577b34da6a3ce929d0e0e4736")
        self.assertTrue(tp.startswith("00-4bf92f3577b34da6a3ce929d0e0e4736-"))
        ids = resolve_ids(headers={"traceparent": tp})
        self.assertEqual(ids.trace_id, "4bf92f3577b34da6a3ce929d0e0e4736")

    def test_gate_default_shadow(self) -> None:
        self.assertEqual(DEFAULT_GATE_MODE, GateMode.SHADOW)
        self.assertEqual(parse_gate_mode(None), GateMode.SHADOW)
        self.assertEqual(parse_gate_mode(""), GateMode.SHADOW)
        self.assertFalse(should_block_writes(None))
        self.assertFalse(should_block_writes("shadow"))
        self.assertTrue(should_block_writes("block"))
        with self.assertRaises(ValueError):
            parse_gate_mode("banana")

    def test_trail_url_doc_compatible(self) -> None:
        url = trail_query_url(
            "http://127.0.0.1:8004",
            TrailQuery(correlation_id="550e8400-e29b-41d4-a716-446655440000"),
        )
        self.assertTrue(url.startswith("http://127.0.0.1:8004/ops/trail?"))
        self.assertIn("correlation_id=550e8400-e29b-41d4-a716-446655440000", url)
        with self.assertRaises(ValueError):
            TrailQuery().validate()

    def test_contract_docs_not_n8n_only(self) -> None:
        """Review-4: CONTRACT.md must not treat n8n nodes as sole truth."""
        for rel in ("docs/zh/CONTRACT.md", "docs/en/CONTRACT.md"):
            text = (ROOT / rel).read_text(encoding="utf-8").lower()
            self.assertIn("n8n", text)  # mentioned as non-truth
            self.assertTrue(
                "不是" in text or "not the contract" in text or "are **not**" in text
                or "are not the contract" in text
            )


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        # Also show example shape for humans / CI logs
        sample = resolve_ids()
        print("OK  example IDs:", json.dumps(sample.as_dict()))
        print("OK  smoke_kit_contract passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
