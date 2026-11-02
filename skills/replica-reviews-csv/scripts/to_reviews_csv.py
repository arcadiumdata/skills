#!/usr/bin/env python3
"""Turn Arcadium review dataset items into reviews.csv (source,url,date,rating,text). Standard library only.

    python3 to_reviews_csv.py --out replica/reviews.csv capterra-items.json trustradius-items.json apps-items.json

Input files are JSON arrays of dataset items from capterra-reviews, trustradius-reviews or software-reviews.
Rows rated --low-max or lower come first, each group newest first. Review words are copied, never rewritten.
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter

SOURCE = {
    "capterra": "capterra",
    "softwareadvice": "capterra",
    "getapp": "getapp",
    "trustradius": "trustradius",
    "googleplay": "google-play",
    "appstore": "app-store",
}


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON array of dataset items")
    return data


def words(value):
    return " ".join(str(value).split()) if value not in (None, "") else ""


def review_text(row):
    parts = [words(row.get("title")), words(row.get("text"))]
    if row.get("pros"):
        parts.append("Pros: " + words(row.get("pros")))
    if row.get("cons"):
        parts.append("Cons: " + words(row.get("cons")))
    return " ".join(p for p in parts if p)


def rating_text(value):
    if not isinstance(value, (int, float)):
        return ""
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="replica/reviews.csv")
    ap.add_argument("--low-max", type=float, default=2.0, help="ratings at or below this go first")
    ap.add_argument("--min-sources", type=int, default=3)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    rows, seen, dropped = [], set(), Counter()
    for path in args.files:
        for item in load(path):
            if item.get("rowType") != "review":
                continue
            key = item.get("reviewId")
            if key and key in seen:
                dropped["repeat"] += 1
                continue
            url = item.get("reviewUrl") or item.get("productUrl")
            text = review_text(item)
            if not url or not text:
                dropped["no url or text"] += 1
                continue
            if key:
                seen.add(key)
            platform = str(item.get("platform") or "unknown").lower()
            rating = item.get("ratingOverall")
            rows.append({
                "source": SOURCE.get(platform, platform),
                "url": url,
                "date": str(item.get("date") or "")[:10],
                "rating": rating_text(rating),
                "text": text,
                "_low": isinstance(rating, (int, float)) and rating <= args.low_max,
            })

    rows.sort(key=lambda r: r["date"], reverse=True)
    rows.sort(key=lambda r: not r["_low"])

    per_source = Counter(r["source"] for r in rows)
    for source, n in per_source.most_common():
        print(f"{source:<14} {n:>5}")
    for reason, n in dropped.items():
        print(f"dropped ({reason}): {n}")
    if len(per_source) < args.min_sources:
        print(f"only {len(per_source)} source(s) have rows; need {args.min_sources}. CSV not written.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["source", "url", "date", "rating", "text"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    low = sum(1 for r in rows if r["_low"])
    print(f"{len(rows)} rows ({low} rated {args.low_max:g} or lower first) written to {args.out}")


if __name__ == "__main__":
    main()
