---
name: hotel-reputation-audit
description: Audit a hotel's online reputation across Tripadvisor, Booking.com, Google Hotels, Agoda and Trip.com - ratings on one 1-5 scale, review counts, recent trend, Booking category scores against the city, recurring guest complaints with quotes, and how often management replies - optionally against competing hotels. Use when the user asks how a hotel is rated, what guests complain about, wants a reputation report, a competitor hotel comparison, review response rate or guest sentiment across booking sites. Runs Arcadium Data actors on Apify with the user's own APIFY_TOKEN (pay per review).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: travel
  keywords: "hotel reviews, hotel reputation, tripadvisor reviews, booking.com reviews, google hotel reviews, agoda reviews, trip.com reviews, guest complaints, review response rate, hospitality"
  apify-actors: "arcadium/hotel-reputation, arcadium/tripadvisor-reviews, arcadium/booking-reviews, arcadium/google-hotel-reviews"
---

# Hotel reputation audit

Read what guests say about a hotel on every major booking and review site, put it on one scale, and write an audit: where the hotel stands, what is getting better or worse, what guests complain about, and whether management answers.

**Disclosure:** the actors this skill runs are built and sold by Arcadium Data, the author of this skill. You pay Apify per review delivered (see Cost). No affiliate codes are used.

## Example prompts

- "Audit the online reputation of The Savoy in London over the last 12 months."
- "Compare guest complaints for my hotel and its three closest competitors on Booking and Tripadvisor."
- "How often does this hotel reply to negative reviews?"

Out of scope:

- Room prices and availability (Arcadium has separate Booking.com prices and Google Hotels actors; they are not part of this skill).
- Reviewer identities: the actors return no reviewer names; Booking, Agoda and Trip.com rows carry only the reviewer's country code.

## Prerequisites

- Apify account and `APIFY_TOKEN`, or `apify login`. Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`).

## Cost

Free Apify plan prices; paid plans pay less. Summary, coverage and error rows are free.

| Actor | Charged event | Free plan | Start fee per run |
| --- | --- | --- | --- |
| `arcadium/hotel-reputation` | `review` | $4.50 per 1,000 | $0.001 |
| `arcadium/tripadvisor-reviews` | `review` | $4.50 per 1,000 | $0.001 |
| `arcadium/booking-reviews` | `review` | $1.80 per 1,000 | $0.001 |
| `arcadium/google-hotel-reviews` | `review` | $0.54 per 1,000 | $0.001 |

Two routes:

- **One run, all sites (`hotel-reputation`):** one dataset, one free summary row per hotel that compares the sites and gives Booking's category scores against the city range. Also covers Agoda and Trip.com. Example: one hotel, 100 reviews each from Tripadvisor, Booking and Google = 300 x $0.0045 + $0.001 = **about $1.35 at most**.
- **Cheaper, one actor per site:** the same 300 reviews = 100 x $0.0045 + 100 x $0.0018 + 100 x $0.00054 + 3 x $0.001 = **about $0.69 at most**. Each actor has its own free summary row, but there is no combined row. Use this route for large pulls, many competitors, or when the user cares about cost.

Tell the user the estimate and ask before runs above $5.

## Workflow

### 1. Identify the hotels

Get each hotel's name with its city, and if possible its Booking.com link (Booking has no name search). Tripadvisor and Google Hotels can be looked up by name.

### 2a. One run, all sites

<!-- input: hotel-reputation -->
```json
{
  "hotels": [
    { "name": "The Savoy London", "bookingUrl": "https://www.booking.com/hotel/gb/the-savoy.html" }
  ],
  "searchGoogleByName": true,
  "maxReviewsPerSource": 100,
  "dateFrom": "2025-11-01"
}
```

    apify actors call arcadium/hotel-reputation --input-file hotels.json --user-agent arcadium-skills/hotel-reputation-audit --json 2>/dev/null
    apify datasets get-items DATASET_ID --format json --user-agent arcadium-skills/hotel-reputation-audit 2>/dev/null > hotel-items.json

(`DATASET_ID` is `.defaultDatasetId` from the call output.) The name is looked up on Tripadvisor (and on Google with `searchGoogleByName`); Booking is read from the link. Add Agoda or Trip.com with `agodaUrl` / `tripcomUrl` in the same object. Competitors are more objects in `hotels` (same run, one start fee).

### 2b. Or one actor per site

<!-- input: tripadvisor-reviews -->
```json
{ "searchQueries": ["The Savoy London"], "maxReviewsPerPlace": 100, "sort": "MOST_RECENT", "dateFrom": "2025-11-01" }
```

<!-- input: booking-reviews -->
```json
{ "startUrls": [{ "url": "https://www.booking.com/hotel/gb/the-savoy.html" }], "maxReviewsPerHotel": 100, "sort": "NEWEST_FIRST", "dateFrom": "2025-11-01", "includeHotelSummary": true }
```

<!-- input: google-hotel-reviews -->
```json
{ "hotels": ["The Savoy London"], "maxReviewsPerHotel": 100, "sort": "newest", "dateFrom": "2025-11-01" }
```

Run each with `apify actors call arcadium/<actor> --input-file <file>.json --user-agent arcadium-skills/hotel-reputation-audit --json 2>/dev/null` and fetch the items the same way. All four actors return the same review row shape.

### 3. Write the audit

Use `rowType: "review"` rows: `platform` (`tripadvisor`, `booking`, `googlehotels`, `agoda`, `tripcom`), `productName`, `date`, `ratingOverall` (1-5 on every site; original in `extras.rawRating` and `extras.rawScale`), `title`, `text`, `pros` and `cons` (Booking: liked / disliked), `vendorResponse` (the hotel's reply), `language`, `country` (reviewer country code on Booking, Agoda, Trip.com), traveler type in `extras.tripType` or `extras.travelerType`. From the free summary rows (`rowType: "hotel-summary"` in `hotel-reputation` and `booking-reviews`): each site's rating and review count, Booking `categoryScores` with `vsCity` (`above`, `within`, `below`).

Sections:

1. **Scorecard:** per site, mean `ratingOverall` of the pulled reviews, the site's own rating and review count from the summary row, and the combined rating.
2. **Trend:** mean rating per month (or quarter) per site; flag a drop of 0.3 or more.
3. **Complaints:** themes from 1-3 star reviews (`cons`, `text`): count, share of low reviews, newest date, and 1-2 short quotes copied exactly. Note when a theme is concentrated in one traveler type or one site.
4. **Strengths:** the same from 4-5 star reviews (`pros`, `text`).
5. **Replies:** share of reviews with a `vendorResponse`, separately for 1-2 star reviews.
6. **Booking categories:** categories `below` the city range.
7. With competitors: the same scorecard side by side, and complaint themes where the hotel is worse than every competitor.

State the review window and caps used (the audit covers the pulled reviews, not every review ever written). Do not name or profile reviewers.

## MCP instead of the CLI

With the Apify MCP server connected, call the actors with the same inputs.

## Troubleshooting

- `error` row `no_match` for a name: give the site's link instead (Tripadvisor `startUrls`, Google `googleUrl`, Booking `bookingUrl`).
- `coverage` row with `shortfall`: the cap or `dateFrom` stopped the run before the site's stated total; `stopReason` says which.
- `blocked` / `unavailable`: retry later; the other inputs in the run are still delivered.
