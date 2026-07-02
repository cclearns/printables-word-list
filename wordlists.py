"""
Shared parsing logic for the Vietnamese Vocabulary Quiz Generator.

Scans word_*.md files for Markdown tables of the form:

    | Tiếng Việt | Tiếng Nhật |
    | --- | --- |
    | từ  | 単語 |

A file can contain more than one such table (e.g. a supplementary
section further down) -- all rows are merged into that file's list.

Used by both server.py (live, for local dev) and build.py (static,
for Netlify deploys).
"""

import re
from pathlib import Path


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


def build_word_lists(folder: Path):
    lessons = {}
    for path in sorted(Path(folder).glob("word_*.md")):
        words = parse_markdown_tables(path.read_text(encoding="utf-8"))
        if words:
            lessons[label_from_filename(path.name)] = words
    return lessons
