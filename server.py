#!/usr/bin/env python3
"""
Tiny local server for the Vietnamese Vocabulary Quiz Generator.

Serves index.html and friends as static files, and exposes
GET /word-lists.json -- a live-scanned JSON dump of every word_*.md
file in this folder (see wordlists.py for the parsing rules).

Add, edit, or remove word_*.md files at any time -- just reload the
page in your browser. No build step required for local dev.

(For deployment, e.g. to Netlify, build.py bakes the same JSON to a
static file at deploy time -- see build.py and netlify.toml.)

Run:
    python3 server.py
Then open:
    http://localhost:8000
"""

import http.server
import json
from pathlib import Path

from wordlists import build_word_lists

FOLDER = Path(__file__).parent
PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FOLDER), **kwargs)

    def do_GET(self):
        if self.path == "/word-lists.json":
            payload = json.dumps(build_word_lists(FOLDER), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass  # keep the console quiet


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Serving {FOLDER} at http://localhost:{PORT}  (Ctrl+C to stop)")
        httpd.serve_forever()
