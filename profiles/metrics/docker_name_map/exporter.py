#!/usr/bin/env python3
"""Map Docker container IDs → names for Grafana legends (OrbStack/cAdvisor).

cAdvisor via containerd often exports name=<id>. This exporter scrapes the
Docker API and exposes docker_container_name_info{id,cname} for PromQL joins.
"""
from __future__ import annotations

import json
import os
import socket
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer

SOCK = os.environ.get("DOCKER_SOCK", "/var/run/docker.sock")
PORT = int(os.environ.get("NAME_MAP_PORT", "9101"))


class UnixHTTPConnection(http.client.HTTPConnection):
    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(SOCK)


def _esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def list_containers() -> list[tuple[str, str]]:
    conn = UnixHTTPConnection("localhost")
    try:
        conn.request("GET", "/containers/json")
        resp = conn.getresponse()
        raw = resp.read()
        if resp.status != 200:
            return []
        data = json.loads(raw.decode("utf-8"))
    finally:
        conn.close()
    out: list[tuple[str, str]] = []
    for c in data:
        cid = c.get("Id") or ""
        names = c.get("Names") or []
        cname = (names[0] if names else cid).lstrip("/")
        if cid and cname:
            out.append((cid, cname))
    return out


def metrics_body() -> bytes:
    lines = [
        "# HELP docker_container_name_info Docker container id to name",
        "# TYPE docker_container_name_info gauge",
    ]
    for cid, cname in list_containers():
        lines.append(
            f'docker_container_name_info{{id="{_esc(cid)}",cname="{_esc(cname)}"}} 1'
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/metrics":
            self.send_response(404)
            self.end_headers()
            return
        body = metrics_body()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
