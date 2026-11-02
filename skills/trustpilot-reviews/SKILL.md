---
name: trustpilot-reviews
description: Get Trustpilot reviews and company ratings as JSON - stars, title, text, date, language, verified flag and the company's reply per review, plus TrustScore, review count, star split and reply rate per company, more than 200 reviews per company, star, language and date filters, and only-new-reviews monitoring. Use when the user asks for Trustpilot reviews, a TrustScore, competitor complaints, review analysis or a weekly review monitor for one or more companies. Runs an Arcadium Data actor on Apify with the user's own APIFY_TOKEN (pay per review).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: reviews
  keywords: "trustpilot reviews, trustpilot scraper, trustscore, customer reviews, competitor reviews, review analysis, complaint mining, review monitoring, company reply rate"
  apify-actors: "arcadium/trustpilot-reviews"
---

# Trustpilot reviews

Trustpilot reviews and company profiles for a list of company domains, returned as JSON rows.

**Disclosure:** the actor this skill runs is built and sold by Arcadium Data, the author of this skill. You pay Apify per review delivered (see Cost). No affiliate codes are used.

## When to use it

- "Get the last 200 Trustpilot reviews of bestbuy.com and list the top complaints."
- "Compare the TrustScore, star split and reply rate of these five competitors."
- "Every Monday, give me only the new 1- and 2-star reviews of our three competitors."

Out of scope:

- Reviewer names, profiles or contact details: the actor never collects them and removes the reviewer's name from review and reply text. Do not try to add them from other sources.
- Reviews only a signed-in user can see. Trustpilot shows an anonymous visitor 200 reviews per filter combination; the actor reaches more through other combinations, not always all of them for very large profiles.

## Prerequisites

- Apify account and `APIFY_TOKEN`, or `apify login`. Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`).

## Cost

Free Apify plan prices; paid plans pay less. With reviews on, the company row, the coverage row and error rows are free; repeats are not charged.

| Actor | Charged event | Free plan | Start fee per run |
| --- | --- | --- | --- |
| `arcadium/trustpilot-reviews` | `review` | $0.52 per 1,000 | $0.005 |
| `arcadium/trustpilot-reviews` | `company` | $2.00 per 1,000 | $0.005 |

The start fee is per GB of memory (about $0.01 at the default 2 GB). `company` is charged only when reviews are switched off (`includeReviews: false`, company rows only). Worked example: 3 companies x 100 reviews = 300 x $0.00052 + about $0.01 = **about $0.17**.

## Workflow

### 1. Build the input

<!-- input: trustpilot-reviews -->
```json
{
  "companies": ["bestbuy.com", "walmart.com"],
  "maxReviewsPerCompany": 100,
  "stars": ["1", "2"],
  "languages": ["en"],
  "includeCompanyInfo": true
}
```

- `companies`: company domains (`bestbuy.com`, `www.zalando.co.uk`) or Trustpilot review page URLs. All companies in one run.
- `maxReviewsPerCompany`: default 100, up to 50,000 (0 = as many as the site shows). Above 200, `splitFilters` (on by default) reads further filter combinations and drops repeats.
- Filters: `stars` (strings `"1"` to `"5"`), `languages` (two-letter codes), `date` (`last30days`, `last3months`, `last6months`, `last12months`) or `dateFrom` (`YYYY-MM-DD`), `verified`, `withReplies`.
- Monitoring: `onlyNewReviews: true` with a fixed `stateKey` (for example `"competitors"`) returns only reviews not delivered by earlier runs with that key, and does not charge repeats. Run it on an Apify schedule.
- Company profiles only: `{"companies": ["bestbuy.com"], "includeReviews": false}` (charged `company` rows).

### 2. Run it

    apify actors call arcadium/trustpilot-reviews --input-file trustpilot.json --user-agent arcadium-skills/trustpilot-reviews --json 2>/dev/null
    apify datasets get-items DATASET_ID --format json --user-agent arcadium-skills/trustpilot-reviews 2>/dev/null > trustpilot.out.json

(`DATASET_ID` is `.defaultDatasetId` from the call output.) Without the CLI: `POST https://api.apify.com/v2/acts/arcadium~trustpilot-reviews/run-sync-get-dataset-items` with header `Authorization: Bearer $APIFY_TOKEN` and the input as the JSON body.

### 3. Read the rows

Filter on `rowType` first.

- `review` rows: `productName` (the company), `entityId` (its Trustpilot domain), `reviewId`, `reviewUrl`, `ratingOverall` (1-5), `title`, `text`, `date`, `language`, `reviewerVerified`, `vendorResponse` (the company's reply, null if none), `helpfulVotes`, `extras.experiencedDate`.
- `company` rows: `name`, `trustScore`, `stars`, `reviewCount`, `reviewCountLast12Months`, `starSplit`, `categories`, `isClaimed`, `replyPercentage`, `averageDaysToReply`, `negativeReviewsTotal`.
- `coverage` rows (free): `stated` (reviews the site states), `delivered`, `stopReason` (`limit`, `end`, `dateFrom`, `onlyNew`, `budget`, `cap` when Trustpilot's limit was reached).
- `error` rows (free): `code` (`not_found`, `blocked`, `unavailable`, `invalid_input`) and `message`.

For complaint analysis, group the 1- and 2-star `text` into themes, count reviews per theme, and quote 1-2 short examples per theme with their `reviewUrl`. Report the sample size and date range from the rows you used; with several languages or `splitFilters`, rows are not in date order, so sort on `date`.

## MCP instead of the CLI

With the Apify MCP server connected, call `arcadium/trustpilot-reviews` with the same input. To expose only this actor as a tool: `https://mcp.apify.com/?tools=arcadium/trustpilot-reviews`.

## Troubleshooting

- `not_found`: the domain has no Trustpilot profile; check the exact domain on trustpilot.com (some companies are listed under `www.` or a country domain).
- `blocked` or `unavailable`: retry the same input later. Do not retry `not_found` or `invalid_input` unchanged.
- Fewer reviews than `stated`: read `stopReason` on the coverage row; `cap` means Trustpilot's anonymous limit was reached for all filter combinations.
