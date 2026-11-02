---
name: competitor-review-mining
description: Mine low-star reviews of competitor software from Capterra, TrustRadius, Google Play and the App Store, save them in the competitor-profiles raw reviews folder layout that the marketingskills competitor-profiling skill reads, and rank the complaints. Use when the user asks what customers hate about a competitor, wants competitor weaknesses, review mining, 1-2 star reviews, churn reasons, switching reasons or battlecard evidence for a B2B SaaS or app. Runs Arcadium Data actors on Apify with the user's own APIFY_TOKEN (pay per review).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: data-extraction
  keywords: "competitor reviews, review mining, capterra reviews, trustradius reviews, app store reviews, google play reviews, negative reviews, complaints, competitor analysis, battlecard"
  apify-actors: "arcadium/capterra-reviews, arcadium/trustradius-reviews, arcadium/software-reviews"
---

# Competitor review mining

Pull the 1-2 star reviews of one or more competitors from four review sites, save them where a competitor-profiling workflow expects them, and turn them into a ranked list of complaints with quotes and links.

**Disclosure:** the actors this skill runs are built and sold by Arcadium Data, the author of this skill. You pay Apify per review delivered, at the prices in the Cost section. No affiliate codes are used.

## Example prompts

- "What do Slack's unhappy customers complain about? Use Capterra and TrustRadius."
- "Mine 1 and 2 star reviews for Asana, Monday.com and ClickUp and rank the complaints."
- "Fill the reviews folder for my competitor-profiling run on Notion."

Out of scope:

- G2 and Gartner Peer Insights reviews (these actors do not read them).
- Trustpilot (consumer brands): Arcadium's Trustpilot reviews actor is not public on the Apify Store yet. This step is added here once it is listed.
- Reviews of the user's own product with reviewer contact details: the actors never return reviewer names, emails or phones.

## Prerequisites

- Apify account and `APIFY_TOKEN` (from [Apify Console > Settings > Integrations](https://console.apify.com/settings/integrations)), or `apify login`.
- Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`).
- Python 3.9+ for `scripts/split_reviews.py` (standard library only).

## Cost

Free Apify plan prices; paid plans pay less per review. Error, coverage and summary rows are free.

| Actor | Charged event | Free plan | Start fee per run |
| --- | --- | --- | --- |
| `arcadium/capterra-reviews` | `review` | $1.79 per 1,000 | $0.001 |
| `arcadium/trustradius-reviews` | `review` | $3.59 per 1,000 | $0.001 |
| `arcadium/software-reviews` | `review` | $1.79 per 1,000 | $0.001 |

Capterra and TrustRadius filter by rating on the site, so you pay only for the low-star reviews you keep. The app-store step (`software-reviews`) has no rating filter: you pay for every review it returns and the helper script drops the high-rated ones afterwards.

Worked example: one competitor, 100 reviews per source (Capterra 1-2 stars, TrustRadius 1-2, Google Play, App Store) = 100 x $0.00179 + 100 x $0.00359 + 200 x $0.00179 + 3 x $0.001 = **about $0.90 at most**. Three competitors in the same three runs: about $2.69 at most. Tell the user the estimate and ask before runs above $5.

## Workflow

### 1. Collect the competitors

For each competitor get the product name and, if possible, its Capterra reviews URL (`https://www.capterra.com/p/<id>/<Name>/reviews/`; a web search for `<name> capterra reviews` finds it). Make a slug: lowercase, hyphenated (`monday-com`). Use today's date as `<YYYY-MM-DD>`.

### 2. Capterra: 1-2 star reviews, newest first

<!-- input: capterra-reviews -->
```json
{
  "startUrls": [{ "url": "https://www.capterra.com/p/135003/Slack/reviews/" }],
  "maxReviewsPerProduct": 100,
  "sort": "MOST_RECENT",
  "maxRating": 2
}
```

    apify actors call arcadium/capterra-reviews --input-file capterra.json --user-agent arcadium-skills/competitor-review-mining --json 2>/dev/null

From the output take `.defaultDatasetId`, then:

    apify datasets get-items DATASET_ID --format json --user-agent arcadium-skills/competitor-review-mining 2>/dev/null > capterra-items.json

Add more competitors as more `startUrls` entries in the same run (one start fee).

### 3. TrustRadius: rating groups 1 and 2

TrustRadius scores 1-10; group `1` is scores 1-2 and group `2` is scores 3-4. `ratingOverall` comes back on a 0-5 scale (score / 2).

<!-- input: trustradius-reviews -->
```json
{
  "products": ["Slack"],
  "maxReviewsPerProduct": 100,
  "starRating": ["1", "2"],
  "sortBy": "date",
  "sortOrder": "desc"
}
```

    apify actors call arcadium/trustradius-reviews --input-file trustradius.json --user-agent arcadium-skills/competitor-review-mining --json 2>/dev/null

Fetch the items as in step 2 into `trustradius-items.json`. A name with no TrustRadius page gives a free `error` row with code `not_found`.

### 4. Google Play and App Store (if the competitor has an app)

<!-- input: software-reviews -->
```json
{
  "products": ["Slack"],
  "sources": ["googleplay", "appstore"],
  "maxReviewsPerSource": 100,
  "sort": "recent"
}
```

    apify actors call arcadium/software-reviews --input-file apps.json --user-agent arcadium-skills/competitor-review-mining --json 2>/dev/null

The app must match the product name (or the vendor); otherwise you get a free `no_match` row instead of a wrong app's reviews. Fetch into `apps-items.json`.

### 5. Save in the competitor-profiles layout

    python3 scripts/split_reviews.py --slug slack --date 2026-11-01 --max-rating 2 capterra-items.json trustradius-items.json apps-items.json

This writes, per review site (named after the `platform` field: `capterra`, `trustradius`, `googleplay`, `appstore`):

```
competitor-profiles/raw/<slug>/<YYYY-MM-DD>/reviews/<platform>.json   # raw review rows, rating <= --max-rating
competitor-profiles/raw/<slug>/<YYYY-MM-DD>/reviews/<platform>.md     # cleaned text: date, rating, title, text, pros, cons, link
```

It refuses to write into a date folder that already has files (snapshots are never overwritten), keeps only `rowType: "review"` rows, and prints per-site counts, mean rating, and any `error` or `coverage` rows with a shortfall. Report those to the user; do not hide a missing source.

### 6. Rank the complaints

Read the `.md` files for each competitor (the `cons` field on Capterra and TrustRadius is the reviewer's own list of downsides; on app stores the complaint is in `text`). Then write `competitor-profiles/_complaints.md`:

1. Group reviews into complaint themes (pricing, missing feature X, performance, support, onboarding, integrations, ...). One review can count for several themes.
2. For each theme: number of reviews, number of sites they came from, mean rating, newest date, and one or two short quotes copied exactly from the review text, each with its `reviewUrl` (or `productUrl` when the review has no own link).
3. Rank themes by review count; mark a theme "thin" when it has fewer than 3 reviews or comes from one site only.
4. Add a per-competitor table and one line per competitor on where it is weakest.

Never invent quotes, counts or reviewers. Do not add reviewer names from other sources. If a source returned nothing, say so in the file.

If the marketingskills `competitor-profiling` skill is in use, its `<slug>.md` profile can now read these files in its review step and list the folder under `## Raw Data Sources`.

## Output fields used

From the review rows (`rowType: "review"`): `platform`, `productName`, `productUrl`, `reviewId`, `reviewUrl`, `title`, `text`, `pros`, `cons`, `ratingOverall` (1-5; TrustRadius 0-5), `date`, `reviewerRole`, `reviewerIndustry`, `reviewerCompanySize`, `switchedFrom`, `reasonForSwitching`, `vendorResponse`. Fields a site does not show are empty, not guessed.

## Calling the actors through MCP instead of the CLI

Connect the Apify MCP server (`https://mcp.apify.com`, with your token) and call `arcadium/capterra-reviews`, `arcadium/trustradius-reviews` and `arcadium/software-reviews` with the same JSON inputs. Save each dataset's items as a JSON array file and continue at step 5.

## Troubleshooting

- `error` row with code `blocked` or `unavailable`: retry that input later. Codes `not_found`, `invalid_input`, `no_match`: fix the input, do not retry as is.
- A `coverage` row with `shortfall` means the site stated more reviews than were delivered (for example the cap was reached). The `stopReason` field says why.
- Few TrustRadius results: try the exact product name from its TrustRadius URL, or pass the URL as `startUrls`.
