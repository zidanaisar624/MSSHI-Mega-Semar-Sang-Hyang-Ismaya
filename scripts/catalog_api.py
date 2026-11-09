#!/usr/bin/env python3
"""Loopback-only, read-only HTTP catalogue for optional MSSHI Actions."""
from __future__ import annotations

import argparse
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


MATRIX = Path(__file__).resolve().parents[1] / "configs" / "bot_role_and_skill_matrix.json"


def catalog_handler(matrix, token):
    # Explicit projection: never serve arbitrary files, source paths or personas.
    skills = {
        item["slug"]: {key: item[key] for key in ("slug", "status", "purpose")}
        for item in matrix["skills"]
    }
    packs = matrix["packs"]

    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            if code == 401:
                self.send_header("WWW-Authenticate", "Bearer")
            if code == 405:
                self.send_header("Allow", "GET")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

        def do_GET(self):
            if token:
                scheme, _, credential = self.headers.get("Authorization", "").partition(" ")
                if scheme.lower() != "bearer" or not hmac.compare_digest(credential.encode(), token.encode()):
                    self.reply(401, {"error": "Bearer token required."})
                    return
            try:
                url = urlsplit(self.path)
                query = parse_qs(url.query, keep_blank_values=True, max_num_fields=4)
            except ValueError:
                self.reply(400, {"error": "Malformed request."})
                return
            if url.path == "/skills":
                selection = query.get("pack", [])
                if set(query) - {"pack"} or len(selection) > 1 or selection == [""]:
                    self.reply(400, {"error": "Use at most one nonempty pack parameter."})
                elif selection and selection[0] not in packs:
                    self.reply(404, {"error": "Pack not found."})
                else:
                    slugs = packs[selection[0]] if selection else skills
                    self.reply(200, {"skills": [skills[slug] for slug in slugs]})
            elif not query and url.path == "/packs":
                self.reply(200, {"packs": [{"id": name, "skills": len(slugs)} for name, slugs in packs.items()]})
            elif not query and url.path.startswith("/skills/") and (slug := unquote(url.path[8:])) in skills:
                self.reply(200, skills[slug])
            else:
                self.reply(404, {"error": "Route or skill not found."})

        def reject_write(self):
            self.reply(405, {"error": "Catalogue supports GET only."})

        do_POST = do_PUT = do_PATCH = do_DELETE = reject_write

    return Handler


def main():
    parser = argparse.ArgumentParser(description="MSSHI read-only catalogue server (localhost only)")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("--port harus 0–65535")
    with MATRIX.open(encoding="utf-8-sig") as handle:
        matrix = json.load(handle)
    token = os.environ.get("MSSHI_CATALOG_TOKEN", "")
    with ThreadingHTTPServer(("127.0.0.1", args.port), catalog_handler(matrix, token)) as server:
        print(f"MSSHI catalogue: http://127.0.0.1:{server.server_port}/skills", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

