#!/usr/bin/env python3
"""Scan the lessons/ folder and write lessons.json for the menu page.

Each lesson describes itself with <meta name="lesson:..."> tags in its <head>.
Everything is optional: without them the lesson is still listed
(title comes from <title>, or from the file name).

Files whose names start with "_" or "." are ignored (drafts, templates).
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
OUT = ROOT / "lessons.json"


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        name = a.get("name") or ""
        if tag == "meta" and name.startswith("lesson:"):
            self.meta[name[len("lesson:"):]] = (a.get("content") or "").strip()
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def to_int(value, default):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def read_lesson(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    end = text.lower().find("</head>")
    head = text[: end + 7] if end != -1 else text[:20000]
    parser = HeadParser()
    parser.feed(head)
    m = parser.meta

    fallback_title = re.sub(r"\s+", " ", parser.title).strip() or path.stem.replace("-", " ").replace("_", " ").title()
    return {
        "title": m.get("title") or fallback_title,
        "grammar": m.get("grammar", ""),
        "desc": m.get("desc", ""),
        "level": m.get("level", ""),
        "minutes": to_int(m.get("minutes"), 0),
        "icon": m.get("icon") or "fa-book",
        "color": m.get("color") or "gold",
        "order": to_int(m.get("order"), 1000),
        "theme": m.get("theme", ""),
        "bg": m.get("bg", ""),
        "accent": m.get("accent", ""),
        "text": m.get("text", ""),
        "href": "lessons/" + path.name,
    }


def main():
    lessons = []
    if LESSONS_DIR.is_dir():
        for path in sorted(LESSONS_DIR.glob("*.htm*")):
            if path.name.startswith(("_", ".")):
                continue
            lessons.append(read_lesson(path))

    lessons.sort(key=lambda l: (l["order"], l["title"].lower()))
    OUT.write_text(json.dumps(lessons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"lessons.json: {len(lessons)} lesson(s)")
    for l in lessons:
        print(f"  - {l['href']}  ->  {l['title']}")


if __name__ == "__main__":
    main()
