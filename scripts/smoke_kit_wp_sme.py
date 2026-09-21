#!/usr/bin/env python3
"""WP SME pilot smoke — ordinary WordPress attach (no n8n).

Checks:
  - GET /obs-health → shadow gate + correlation_id
  - Homepage reachable (200/302/301)
  - Optional: Loki has recent lines for kit_pilot=wp-sme (requires loki profile)

Env:
  WP_SME_URL          default http://127.0.0.1:8087
  OBS_LOKI_URL        default http://127.0.0.1:3100
  OBS_SMOKE_SKIP_LOKI=1  skip Loki assert

Exit 0 = pass.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class Fail(Exception):
    pass


def _ok(msg: str) -> None:
    print(f"OK  {msg}")


def _warn(msg: str) -> None:
    print(f"WARN {msg}")


def _base() -> str:
    return os.getenv("WP_SME_URL", "http://127.0.0.1:8087").rstrip("/")


def _loki() -> str:
    return os.getenv("OBS_LOKI_URL", "http://127.0.0.1:3100").rstrip("/")


def _get_json(url: str, *, timeout: float = 15.0) -> tuple[dict[str, Any], dict[str, str]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            raw = resp.read().decode()
            data = json.loads(raw) if raw else {}
            if not isinstance(data, dict):
                raise Fail(f"expected JSON object from {url}")
            return data, headers
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        raise Fail(f"HTTP {exc.code} GET {url}\n{body}") from exc
    except urllib.error.URLError as exc:
        raise Fail(f"unreachable {url}: {exc}") from exc


def _get_status(url: str, *, timeout: float = 15.0) -> int:
    req = urllib.request.Request(url, method="GET")
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except urllib.error.URLError as exc:
        raise Fail(f"unreachable {url}: {exc}") from exc


def _wait_health(timeout_s: float = 120.0) -> dict[str, Any]:
    url = f"{_base()}/obs-health/"

    deadline = time.time() + timeout_s
    last = ""
    while time.time() < deadline:
        try:
            data, headers = _get_json(url)
            corr_h = headers.get("x-correlation-id", "")
            if data.get("obs_quality_gate_mode") != "shadow":
                raise Fail(f"gate mode want shadow, got {data.get('obs_quality_gate_mode')!r}")
            if data.get("obs_quality_gate_blocks_writes") is not False:
                raise Fail("obs_quality_gate_blocks_writes must be false in shadow")
            cid = data.get("correlation_id")
            if not isinstance(cid, str) or len(cid) < 32:
                raise Fail(f"bad correlation_id: {cid!r}")
            if corr_h and corr_h.lower() != cid.lower():
                raise Fail(f"header X-Correlation-Id {corr_h!r} != body {cid!r}")
            _ok(f"/obs-health shadow + correlation_id={cid}")
            return data
        except Fail as exc:
            last = str(exc)
            time.sleep(2.0)
    raise Fail(f"timeout waiting for /obs-health\n{last}")


def _assert_home() -> None:
    code = _get_status(_base() + "/")
    if code not in (200, 301, 302, 303, 307, 308):
        raise Fail(f"homepage unexpected HTTP {code}")
    _ok(f"homepage HTTP {code}")


def _assert_loki() -> None:
    if os.getenv("OBS_SMOKE_SKIP_LOKI", "").strip() in ("1", "true", "yes"):
        _warn("skip Loki assert (OBS_SMOKE_SKIP_LOKI)")
        return
    # Generate a bit of traffic + unique marker in query string (appears in access log)
    marker = f"obs-kit-wp-sme-{int(time.time())}"
    try:
        _get_status(f"{_base()}/?{marker}")
    except Fail:
        pass
    time.sleep(3.0)

    # Prefer pilot label; fall back to container name regex
    queries = [
        '{kit_pilot="wp-sme"}',
        '{container=~".*wordpress.*"}',
    ]
    end_ns = int(time.time() * 1e9)
    start_ns = end_ns - int(10 * 60 * 1e9)
    last_err = ""
    for q in queries:
        qs = urllib.parse.urlencode(
            {
                "query": q,
                "start": start_ns,
                "end": end_ns,
                "limit": "50",
            }
        )
        url = f"{_loki()}/loki/api/v1/query_range?{qs}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with _OPENER.open(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode())
            results = (payload.get("data") or {}).get("result") or []
            if results:
                _ok(f"Loki query hit ({q}) streams={len(results)}")
                return
            last_err = f"no streams for {q}"
        except urllib.error.URLError as exc:
            last_err = f"Loki unreachable: {exc}"
            break
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
    raise Fail(
        "Loki has no WP SME lines — is `bootstrap up --profile loki` running?\n"
        f"  last={last_err}\n"
        "  or set OBS_SMOKE_SKIP_LOKI=1"
    )


def main() -> int:
    try:
        _wait_health()
        _assert_home()
        _assert_loki()
        print("OK  smoke_kit_wp_sme passed")
        return 0
    except Fail as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
