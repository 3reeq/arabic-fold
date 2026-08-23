#!/usr/bin/env python3
"""Check the Python fold against pairs.json — the shared contract.

The JS implementation in demo/ is checked against the SAME file by
demo/test.html. That is what keeps them from drifting.

    python3 test_fold.py
"""

import json
import sqlite3
import sys
from pathlib import Path

from arabic_fold import index_text, search_text

PAIRS = json.loads((Path(__file__).parent / "pairs.json").read_text(encoding="utf-8"))

failed = 0


def check(label, got, want):
    global failed
    ok = got == want
    if not ok:
        failed += 1
        print(f"  FAIL  {label}\n        got  {got!r}\n        want {want!r}")
    return ok


print("fold_ar")
for case in PAIRS["fold_ar"]:
    check(case["note"], index_text(case["in"]), case["out"])
print(f"  {len(PAIRS['fold_ar'])} cases")

print("fold_latin")
for case in PAIRS["fold_latin"]:
    check(case["note"], index_text(case["in"]), case["out"])
print(f"  {len(PAIRS['fold_latin'])} cases")

# index_text and search_text must be the same transform. If someone ever
# "optimises" one of them, this is what catches it.
print("both sides agree")
for case in PAIRS["fold_ar"] + PAIRS["fold_latin"]:
    check(f"index/search disagree on {case['in']!r}",
          index_text(case["in"]), search_text(case["in"]))
print("  ok")

# The end-to-end claim the README makes: 5/9, 5/9, 9/9.
demo = PAIRS["_search_demo"]


def score(fold_index, fold_query):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE VIRTUAL TABLE fts USING fts5(name)")
    db.executemany("INSERT INTO fts(name) VALUES (?)",
                   [(index_text(r["text"]) if fold_index else r["text"],)
                    for r in demo["records"]])
    hits = 0
    for q in demo["queries"]:
        term = search_text(q["text"]) if fold_query else q["text"]
        hits += db.execute("SELECT count(*) FROM fts WHERE fts MATCH ?",
                           (term + "*",)).fetchone()[0]
    return hits


print("end-to-end")
check("fold neither side", score(False, False), 5)
check("fold index only",   score(True, False), 5)
check("fold both sides",   score(True, True), 9)
print("  neither=5/9  index-only=5/9  both=9/9")

print()
if failed:
    sys.exit(f"{failed} failure(s)")
print("all passed")
