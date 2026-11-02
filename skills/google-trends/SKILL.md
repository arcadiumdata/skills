---
name: google-trends
description: Get Google Trends data as JSON - interest over time, interest by region, related and rising queries, related topics, more than 5 keywords on one scale, and today's Trending now searches for a country. Use when the user asks for Google Trends numbers, search interest, seasonality, keyword or brand comparisons, rising queries or what is trending, when pytrends fails with 429 Too Many Requests, or when a web fetch of trends.google.com returns no numbers. Runs an Arcadium Data actor on Apify with the user's own APIFY_TOKEN (pay per keyword row).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: marketing
  keywords: "google trends, pytrends, pytrends alternative, search interest, interest over time, rising queries, related queries, trending now, seasonality, keyword comparison"
  apify-actors: "arcadium/google-trends"
---

# Google Trends

Google Trends numbers for any keyword, country and period, read in the Apify cloud and returned as one JSON row per keyword.

**Disclosure:** the actor this skill runs is built and sold by Arcadium Data, the author of this skill. You pay Apify per row delivered (see Cost). No affiliate codes are used.

## When to use it

- The user wants Google Trends data, not an opinion: "Compare US interest in notion vs obsidian over 12 months", "Which states search most for heat pumps?", "What is rising around 'protein ice cream'?", "What is trending in Germany right now?".
- A local `pytrends` script fails with `TooManyRequestsError` (Google returned HTTP 429). This actor takes the same parameters and runs the requests through Apify proxies with retries, off the user's IP.
- `web_fetch` of `trends.google.com` returns a page without the numbers (the charts are loaded by script).

Out of scope:

- Absolute search volumes. Google Trends values are relative interest from 0 to 100; Trending now gives only a volume bracket such as `100,000+`. Never present them as search counts.
- Data behind a login (the actor reads public Google Trends only).

## Prerequisites

- Apify account and `APIFY_TOKEN`, or `apify login`. Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`).

## Cost

Free Apify plan prices; paid plans pay less. Error rows (`rowType: "error"`) are free.

| Actor | Charged event | Free plan | Start fee per run |
| --- | --- | --- | --- |
| `arcadium/google-trends` | `result` | $2.70 per 1,000 | $0.00005 |

One row per keyword (or per Trending now search). Worked example: 5 keywords compared on one scale = 5 x $0.0027 + $0.00005 = **about $0.014**.

## Workflow

### 1. Build the input

<!-- input: google-trends -->
```json
{
  "searchTerms": ["notion", "obsidian"],
  "compareKeywords": true,
  "geo": "US",
  "includeRelatedQueries": true,
  "includeRelatedTopics": false,
  "includeGeo": false
}
```

- `searchTerms`: one row per keyword. Put all keywords in one run (one start fee).
- `compareKeywords: true` puts all keywords on one 0-100 scale. Use it whenever the user compares terms; without it each keyword is scaled to its own peak and values of two keywords cannot be compared. Above 5 keywords the actor batches them with a shared anchor keyword (`anchorKeyword`, default the first one); `scale` on each row says whether values are exact or approximate.
- `geo`: `US`, `GB`, `DE`, a region such as `US-CA`, or empty for worldwide.
- Period: leave `timeRange` out for the past 12 months, or use a preset (`now 7-d`, `today 1-m`, `today 3-m`, `today 5-y`, `all`), or `customTimeRange` as `"2024-01-01 2024-12-31"`.
- `includeGeo: true` adds interest by country, subregion or city (Google picks the level). `includeRelatedTopics: true` adds related topics.
- `property`: `images`, `news`, `youtube` or `froogle` (shopping) instead of web search.
- What is trending now: `{"trendingGeos": ["US"], "trendingHours": "24"}` gives one row per trending search.

From pytrends: `build_payload(kw_list, cat, timeframe, geo, gprop)` maps to `searchTerms`, `category`, `timeRange` or `customTimeRange`, `geo` and `property`.

### 2. Run it

    apify actors call arcadium/google-trends --input-file trends.json --user-agent arcadium-skills/google-trends --json 2>/dev/null
    apify datasets get-items DATASET_ID --format json --user-agent arcadium-skills/google-trends 2>/dev/null > trends-rows.json

(`DATASET_ID` is `.defaultDatasetId` from the call output.) Without the CLI, one HTTP call returns the rows: `POST https://api.apify.com/v2/acts/arcadium~google-trends/run-sync-get-dataset-items` with header `Authorization: Bearer $APIFY_TOKEN` and the input as the JSON body.

### 3. Read the rows

Filter on `rowType` first.

- `trend` rows: `searchTerm`, `geo`, `timeRange`, `averageInterest` (mean of the timeline), `interestOverTime_timelineData` (points with `time` in Unix seconds, `formattedTime`, `value` as a one-number array, `isPartial` on the unfinished last point), `interestBy` / `interestBySubregion` / `interestByCity`, `relatedQueries_top`, `relatedQueries_rising` (`formattedValue` such as `+250%` or `Breakout`), `relatedTopics_top`, `relatedTopics_rising`, `scale`.
- Trending now rows: `keyword`, `geo`, `searchVolume` (lower bound of Google's bracket), `increasePercent`, `startedAt`, `active`, `relatedKeywords`.
- `error` rows (free): `code` and `message`.

Answer with the numbers: averages, peaks with their dates, the trend direction (compare the last 3 months with the same months a year earlier for seasonal terms), and the rising queries. Say that values are relative (0-100). Ignore the `isPartial` last point when judging a recent change.

## MCP instead of the CLI

With the Apify MCP server connected, call `arcadium/google-trends` with the same input. To expose only this actor as a tool: `https://mcp.apify.com/?tools=arcadium/google-trends`.

## Troubleshooting

- `code: "blocked"`: Google kept answering "too many requests" after all retries. The row is free; run those keywords again later. The actor slows itself down when Google limits the shared proxy pool, so long lists can take a few minutes longer on such a day.
- `code: "no_match"`: the keyword has too little search volume in that place and period. Try a broader term, a longer period or worldwide.
- `code: "invalid_input"`: check `geo`, `category` and the `customTimeRange` format.
- Two runs of the same keyword differ slightly: Google samples its data, and the last point of a period is still being filled in.
