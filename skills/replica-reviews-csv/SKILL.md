---
name: replica-reviews-csv
description: Build reviews.csv (columns source,url,date,rating,text) for an app or SaaS product from at least three review sites - Capterra, TrustRadius, Google Play and the App Store - with low-rated and recent reviews first, in the format the replica-entrepreneur skill's reviews.py ranker reads. Use when the user needs 100+ real reviews of a product in one CSV, wants to feed a feedback ranker, or asks to collect what users hate about an app before cloning or competing with it. Runs Arcadium Data actors on Apify with the user's own APIFY_TOKEN (pay per review).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: data-extraction
  keywords: "reviews csv, app reviews, capterra reviews, trustradius reviews, google play reviews, app store reviews, user feedback, replica-entrepreneur, complaints"
  apify-actors: "arcadium/capterra-reviews, arcadium/trustradius-reviews, arcadium/software-reviews"
---

# Reviews CSV for replica-entrepreneur

Collect real reviews of one product from three or four review sites and write `replica/reviews.csv` with the columns `source,url,date,rating,text`: low-rated reviews first, newest first inside each group.

**Disclosure:** the actors this skill runs are built and sold by Arcadium Data, the author of this skill. You pay Apify per review delivered (see Cost). No affiliate codes are used.

**About replica-entrepreneur.** That skill asks for reviews collected by reading, and says it does not run scrapers against stores or review sites whose terms forbid it. This skill is a separate data source that the user chooses to run on their own Apify account; it is not part of replica-entrepreneur and not endorsed by its author. Tell the user this and let them decide.

## Example prompts

- "Get me 200 reviews of Notion from Capterra, TrustRadius and the app stores as reviews.csv."
- "Build replica/reviews.csv for Todoist, recent and 1-2 star reviews first."

Out of scope:

- G2, Reddit, Hacker News and Product Hunt (not covered by these actors; add those rows by hand if needed).
- Trustpilot: Arcadium's Trustpilot reviews actor is not public on the Apify Store yet.

## Prerequisites

- Apify account and `APIFY_TOKEN`, or `apify login`. Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`).
- Python 3.9+ for `scripts/to_reviews_csv.py` (standard library only).

## Cost

Free Apify plan prices; paid plans pay less. Error, coverage and summary rows are free.

| Actor | Charged event | Free plan | Start fee per run |
| --- | --- | --- | --- |
| `arcadium/capterra-reviews` | `review` | $1.79 per 1,000 | $0.001 |
| `arcadium/trustradius-reviews` | `review` | $3.59 per 1,000 | $0.001 |
| `arcadium/software-reviews` | `review` | $1.79 per 1,000 | $0.001 |

Worked example: 50 reviews from each of Capterra, TrustRadius, Google Play and the App Store (200 rows) = 50 x $0.00179 + 50 x $0.00359 + 100 x $0.00179 + 3 x $0.001 = **about $0.45 at most**. Ask the user before runs above $5.

## Workflow

Replace `Slack` with the product. Set `dateFrom` to about 18 months ago (replica-entrepreneur counts older reviews at half weight).

### 1. Capterra

<!-- input: capterra-reviews -->
```json
{
  "startUrls": [{ "url": "https://www.capterra.com/p/135003/Slack/reviews/" }],
  "maxReviewsPerProduct": 50,
  "sort": "MOST_RECENT",
  "dateFrom": "2025-05-01"
}
```

    apify actors call arcadium/capterra-reviews --input-file capterra.json --user-agent arcadium-skills/replica-reviews-csv --json 2>/dev/null
    apify datasets get-items DATASET_ID --format json --user-agent arcadium-skills/replica-reviews-csv 2>/dev/null > capterra-items.json

(`DATASET_ID` is `.defaultDatasetId` from the call output.) No Capterra URL at hand? Use `software-reviews` with `"sources": ["capterra", "googleplay", "appstore"]`, which looks the name up and returns the same Capterra reviews.

### 2. TrustRadius

<!-- input: trustradius-reviews -->
```json
{
  "products": ["Slack"],
  "maxReviewsPerProduct": 50,
  "sortBy": "date",
  "sortOrder": "desc",
  "dateFrom": "2025-05-01"
}
```

    apify actors call arcadium/trustradius-reviews --input-file trustradius.json --user-agent arcadium-skills/replica-reviews-csv --json 2>/dev/null

Fetch into `trustradius-items.json` as above.

### 3. Google Play and App Store

<!-- input: software-reviews -->
```json
{
  "products": ["Slack"],
  "sources": ["googleplay", "appstore"],
  "maxReviewsPerSource": 50,
  "sort": "recent",
  "dateFrom": "2025-05-01"
}
```

    apify actors call arcadium/software-reviews --input-file apps.json --user-agent arcadium-skills/replica-reviews-csv --json 2>/dev/null

Fetch into `apps-items.json`. An app that does not match the product name gives a free `no_match` row, not a wrong app.

### 4. Write the CSV

    python3 scripts/to_reviews_csv.py --out replica/reviews.csv capterra-items.json trustradius-items.json apps-items.json

The script:

- keeps `rowType: "review"` rows and drops repeats by `reviewId`;
- maps `platform` to the source names reviews.py uses: `capterra`, `trustradius`, `google-play`, `app-store`;
- `url` is the review's own link (`reviewUrl`), else the product's review page (`productUrl`); rows with neither, or with no text, are dropped and counted;
- `date` is `YYYY-MM-DD`; `rating` is `ratingOverall` on a 1-5 scale (TrustRadius 0-5 in half steps);
- `text` is the review's own words: `title`, `text`, then `Pros:` and `Cons:` when the site splits them out. Nothing is paraphrased;
- orders rows rated 2 or lower first (`--low-max` to change), each group newest first;
- prints rows per source and fails if fewer than 3 sources have rows (`--min-sources` to change).

Then run replica-entrepreneur's own ranker on the file (`python3 reviews.py replica/reviews.csv --out replica/feedback.md`).

## Output fields used

`platform`, `reviewId`, `reviewUrl`, `productUrl`, `date`, `ratingOverall`, `title`, `text`, `pros`, `cons` from review rows. No reviewer names or contact details are in the data or the CSV.

## MCP instead of the CLI

With the Apify MCP server connected, call the three actors with the same inputs, save each dataset's items as a JSON array file, and run step 4.

## Troubleshooting

- `error` rows: `blocked` / `unavailable` mean retry later; `not_found`, `invalid_input`, `no_match` mean fix the input.
- Fewer than 3 sources: add `softwareadvice` to `sources`, or a second product name the sites use.
