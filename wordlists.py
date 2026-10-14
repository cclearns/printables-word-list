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


# --- Google Sheet words (Lớp A / Lớp B) -------------------------------------

SHEET_ID = "1j0pzmkdrrA5iwhoNOAgYncC33RdqMDoitSd6b9yv39M"
SHEET_TABS = {"Lớp A": "837535482", "Lớp B": "0"}  # tab name -> gid


def parse_sheet_csv(text: str):
    """Rows are: Loại từ, Tiếng Việt, Tiếng Nhật, Chú ý. Keep rows with both languages."""
    import csv
    import io

    words = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 3:
            continue
        vi, jp = row[1].strip(), row[2].strip()
        if not vi or not jp or vi.lower() in ("tiếng việt", "vietnamese"):
            continue
        words.append({"vi": vi, "jp": jp})
    return words


def fetch_sheet_words(timeout: int = 20):
    """Download each tab of the public Google Sheet as CSV. A tab that fails is omitted."""
    from urllib.request import urlopen

    tabs = {}
    for name, gid in SHEET_TABS.items():
        url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
               f"/export?format=csv&gid={gid}")
        try:
            with urlopen(url, timeout=timeout) as res:
                words = parse_sheet_csv(res.read().decode("utf-8"))
        except Exception as err:
            print(f"Could not fetch Google Sheet tab {name}: {err}")
            continue
        if words:
            tabs[name] = words
    return tabs
