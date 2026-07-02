#!/usr/bin/env python3
"""
Tiny local server for the Vietnamese Vocabulary Quiz Generator.

Serves index.html and friends as static files, and exposes
GET /api/word-lists -- a live-scanned JSON dump of every word_*.md
file in this folder, parsed from Markdown tables of the form:

    | Tiếng Việt | Tiếng Nhật |
    | --- | --- |
    | từ  | 単語 |

A file can contain more than one such table (e.g. a supplementary
section further down) -- all rows are merged into that file's list.

Add, edit, or remove word_*.md files at any time -- just reload the
page in your browser. No build step required.

Run:
    python3 server.py
Then open:
    http://localhost:8000
"""

import http.server
import json
import re
from pathlib import Path

FOLDER = Path(__file__).parent
PORT = 8000


def label_from_filename(filename: str) -> str:
    """word_bai1.md -> Bài 1 ; word_Bai_24_TuVung.md -> Bài 24 ; word_x.md -> x"""
    base = re.sub(r"\.md$", "", filename, flags=re.IGNORECASE)
    base = re.sub(r"^word_", "", base, flags=re.IGNORECASE)
    m = re.search(r"bai[_\s]?(\d+)", base, flags=re.IGNORECASE)
    if m:
        return f"Bài {int(m.group(1))}"
    return base.replace("_", " ").strip() or filename


def parse_markdown_tables(text: str):
    """Extract every `| Vietnamese | Japanese |` data row from all tables in the file."""
    words = []
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or not cells[0]:
            continue
        if cells[0].lower() in ("tiếng việt", "vietnamese"):
            continue  # header row
        if re.fullmatch(r"[-:\s]+", cells[0]):
            continue  # alignment row (---|---)
        words.append({"vi": cells[0], "jp": cells[1]})
    return words


def build_word_lists():
    lessons = {}
    for path in sorted(FOLDER.glob("word_*.md")):
        words = parse_markdown_tables(path.read_text(encoding="utf-8"))
        if words:
            lessons[label_from_filename(path.name)] = words
    return lessons


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FOLDER), **kwargs)

    def do_GET(self):
        if self.path == "/api/word-lists":
            payload = json.dumps(build_word_lists(), ensure_ascii=False).encode("utf-8")
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
