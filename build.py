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

from wordlists import build_word_lists

FOLDER = Path(__file__).parent
OUTPUT = FOLDER / "word-lists.json"


def main():
    lessons = build_word_lists(FOLDER)
    OUTPUT.write_text(json.dumps(lessons, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT.name} with {len(lessons)} list(s), "
          f"{sum(len(w) for w in lessons.values())} words total.")


if __name__ == "__main__":
    main()
