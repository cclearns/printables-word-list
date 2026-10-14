#!/usr/bin/env python3
"""
Build step for static hosting (e.g. Netlify).

Scans word_*.md and writes word-lists.json -- the same data
server.py serves live at /word-lists.json for local dev. Netlify
runs this automatically before every deploy (see netlify.toml), so
you never have to run it by hand -- just push to GitHub.
"""

import json
from pathlib import Path

from wordlists import build_word_lists, fetch_sheet_words

FOLDER = Path(__file__).parent
OUTPUT = FOLDER / "word-lists.json"
SHEET_OUTPUT = FOLDER / "sheet-words.json"


def main():
    lessons = build_word_lists(FOLDER)
    OUTPUT.write_text(json.dumps(lessons, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT.name} with {len(lessons)} list(s), "
          f"{sum(len(w) for w in lessons.values())} words total.")

    # Google Sheet (Lớp A / Lớp B). If the fetch fails the quiz still works
    # -- the page just skips the sheet words.
    sheet = fetch_sheet_words()
    SHEET_OUTPUT.write_text(json.dumps(sheet, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {SHEET_OUTPUT.name}: "
          + ", ".join(f"{k} {len(v)}" for k, v in sheet.items()))


if __name__ == "__main__":
    main()
