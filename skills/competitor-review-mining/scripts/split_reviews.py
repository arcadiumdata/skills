#!/usr/bin/env python3
"""Split review dataset items into the competitor-profiles layout. Standard library only.

    python3 split_reviews.py --slug slack --date 2026-11-01 --max-rating 2 capterra-items.json trustradius-items.json

Input files are JSON arrays of dataset items from the Arcadium review actors on Apify
(capterra-reviews, trustradius-reviews, software-reviews). Only rows with rowType "review" and
ratingOverall <= --max-rating are kept. Writes, per platform:

    <out>/raw/<slug>/<date>/reviews/<platform>.json   raw rows
    <out>/raw/<slug>/<date>/reviews/<platform>.md     cleaned text with links

A date folder that already holds files is never overwritten. Nothing is invented: empty fields stay empty.
"""

import argparse
import json
import os
import re
import sys

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SAFE = re.compile(r"[^a-z0-9-]+")


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON array of dataset items")
    return data


def clean(value):
    return " ".join(str(value).split()) if value not in (None, "") else ""


def to_md(platform, rows):
    lines = [f"# {platform} reviews ({len(rows)})", ""]
    for r in rows:
        link = r.get("reviewUrl") or r.get("productUrl") or ""
        head = f"## {clean(r.get('date'))[:10]} | rating {r.get('ratingOverall')}"
        if r.get("title"):
            head += f" | {clean(r.get('title'))}"
        lines.append(head)
        for label, key in (("Text", "text"), ("Pros", "pros"), ("Cons", "cons")):
            if r.get(key):
                lines.append(f"- {label}: {clean(r.get(key))}")
        for label, key in (("Role", "reviewerRole"), ("Company size", "reviewerCompanySize"), ("Industry", "reviewerIndustry")):
            if r.get(key):
                lines.append(f"- {label}: {clean(r.get(key))}")
        if link:
            lines.append(f"- Link: {link}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="competitor slug, lowercase and hyphenated")
    ap.add_argument("--date", required=True, help="pull date, YYYY-MM-DD")
    ap.add_argument("--max-rating", type=float, default=2.0, help="keep reviews rated at most this (1-5 scale)")
    ap.add_argument("--out", default="competitor-profiles", help="root folder (default competitor-profiles)")
    ap.add_argument("files", nargs="+", help="dataset item files (JSON arrays)")
    args = ap.parse_args()

    if not SLUG.match(args.slug):
        raise SystemExit("--slug must be lowercase and hyphenated, e.g. monday-com")
    if not DATE.match(args.date):
        raise SystemExit("--date must be YYYY-MM-DD")

    target = os.path.join(args.out, "raw", args.slug, args.date, "reviews")
    if os.path.isdir(target) and os.listdir(target):
        raise SystemExit(f"{target} already has files; use a new date folder instead of overwriting a snapshot")

    by_platform, notes, dropped = {}, [], 0
    for path in args.files:
        for row in load(path):
            kind = row.get("rowType")
            if kind == "review":
                rating = row.get("ratingOverall")
                if not isinstance(rating, (int, float)) or rating > args.max_rating:
                    dropped += 1
                    continue
                platform = SAFE.sub("-", str(row.get("platform") or "unknown").lower()).strip("-") or "unknown"
                by_platform.setdefault(platform, []).append(row)
            elif kind == "error":
                notes.append(f"error {row.get('code')}: {row.get('message')} (input {json.dumps(row.get('input'))})")
            elif kind == "coverage" and row.get("shortfall"):
                notes.append(
                    f"coverage {row.get('platform')}: stated {row.get('stated')}, delivered {row.get('delivered')}, "
                    f"stop {row.get('stopReason')}"
                )

    os.makedirs(target, exist_ok=True)
    print(f"{'platform':<14} {'kept':>5} {'mean':>5}")
    for platform, rows in sorted(by_platform.items()):
        rows.sort(key=lambda r: str(r.get("date") or ""), reverse=True)
        with open(os.path.join(target, f"{platform}.json"), "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)
        with open(os.path.join(target, f"{platform}.md"), "w", encoding="utf-8") as fh:
            fh.write(to_md(platform, rows))
        mean = sum(r["ratingOverall"] for r in rows) / len(rows)
        print(f"{platform:<14} {len(rows):>5} {mean:>5.2f}")
    print(f"dropped (rated above {args.max_rating} or unrated): {dropped}")
    for note in notes:
        print(note, file=sys.stderr)
    if not by_platform:
        print("no reviews kept; check the error rows above", file=sys.stderr)
    print(f"written to {target}")


if __name__ == "__main__":
    main()
