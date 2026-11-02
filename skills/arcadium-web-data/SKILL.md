---
name: arcadium-web-data
description: Pick and run the right Apify actor for public web data - Amazon, Etsy and 1688 products, Booking.com and Google Hotels prices, hotel reviews (Tripadvisor, Booking.com, Google, Agoda, Trip.com), Yelp, Capterra, TrustRadius, Google Play and App Store reviews, Google Trends, Google News, YouTube videos and transcripts, company job postings from career sites, Seek jobs, ATS detection and AutoScout24 used cars. Use when the user asks to scrape, collect, monitor or export any of these. Gives the actor ID, a small input that works on the first run, and the price. Runs Arcadium Data actors on Apify with the user's own APIFY_TOKEN (pay per result).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: data
  keywords: "web scraping, apify actor, amazon products, hotel prices, hotel reviews, tripadvisor reviews, booking.com, google trends, google news, youtube transcript, job postings, capterra reviews, used cars"
  apify-actors: "arcadium/amazon-products, arcadium/etsy-products, arcadium/1688-products, arcadium/booking-prices, arcadium/google-hotels, arcadium/hotel-reputation, arcadium/tripadvisor-reviews, arcadium/booking-reviews, arcadium/google-hotel-reviews, arcadium/agoda-tripcom-reviews, arcadium/yelp-reviews, arcadium/capterra-reviews, arcadium/capterra-products, arcadium/trustradius-reviews, arcadium/software-reviews, arcadium/reputation-monitor, arcadium/google-trends, arcadium/google-news, arcadium/youtube-videos, arcadium/youtube-transcripts, arcadium/career-site-jobs, arcadium/ats-lookup, arcadium/seek-jobs, arcadium/eu-car-listings"
---

# Arcadium web data (actor router)

One table from a data request to the actor ID, a first input that works, and the price. Start small (the inputs below return 10 to 50 rows), check the rows, then raise the limit.

**Disclosure:** the actors this skill routes to are built and sold by Arcadium Data, the author of this skill. You pay Apify per result with your own account (see Cost). No affiliate codes are used.

## Prerequisites

- Apify account and `APIFY_TOKEN`, or `apify login`. Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`, tool `call-actor` with the actor ID below).

## How to run

```bash
apify actors call arcadium/<actor> --input-file input.json --user-agent arcadium-skills/arcadium-web-data --json 2>/dev/null
```

Then read the dataset items of the run. Rows with `rowType` `error`, `coverage` or `summary` are free and explain gaps (blocked page, site limit reached); report them, do not retry blindly.

## Which actor

| User asks for | Actor | First input | Charged event, free plan |
| --- | --- | --- | --- |
| Amazon search results, product data, Best Sellers | `arcadium/amazon-products` | `{"searches": ["wireless earbuds"], "marketplace": "US", "maxResultsPerSearch": 20}` | `search-result` $0.54 / 1,000 (`product` $2.25, `bestseller` $5.31) |
| Etsy listings, prices, tags, shop sales | `arcadium/etsy-products` | `{"searchTerms": ["ceramic mug"], "maxResultsPerSearch": 20}` | `listing` $7.20 / 1,000 |
| 1688.com wholesale prices, MOQ, factories | `arcadium/1688-products` | `{"keywords": ["保温杯"], "maxItemsPerKeyword": 50}` | `product` $1.80 / 1,000 |
| Booking.com hotel prices and availability by date | `arcadium/booking-prices` | `{"startUrls": [{"url": "https://www.booking.com/hotel/fr/de-la-paix-paris1.html"}], "checkInDates": ["+30d"], "nights": [1], "currency": "EUR"}` | `result` $2.70 / 1,000 |
| Google Hotels prices, ratings, booking offers | `arcadium/google-hotels` | `{"locations": ["Paris"], "checkInDates": ["+30d"], "nights": [2], "maxHotels": 20}` | `hotel` $4.49 / 1,000 |
| One hotel across Tripadvisor, Booking.com and Google | `arcadium/hotel-reputation` | `{"hotels": [{"name": "The Savoy London", "bookingUrl": "https://www.booking.com/hotel/gb/the-savoy.html"}], "maxReviewsPerSource": 20}` | `review` $4.50 / 1,000 |
| Tripadvisor reviews (hotels, restaurants, attractions) | `arcadium/tripadvisor-reviews` | `{"searchQueries": ["hyatt grand central new york"], "maxReviewsPerPlace": 20}` | `review` $4.50 / 1,000 |
| Booking.com reviews | `arcadium/booking-reviews` | `{"startUrls": [{"url": "https://www.booking.com/hotel/gb/the-savoy.html"}], "maxReviewsPerHotel": 20, "sort": "NEWEST_FIRST"}` | `review` $1.80 / 1,000 |
| Google hotel reviews | `arcadium/google-hotel-reviews` | `{"hotels": ["Hotel Adlon Kempinski Berlin"], "maxReviewsPerHotel": 20, "sort": "newest"}` | `review` $0.54 / 1,000 |
| Agoda or Trip.com hotel reviews | `arcadium/agoda-tripcom-reviews` | `{"startUrls": [{"url": "https://www.agoda.com/ibis-bangkok-riverside/hotel/bangkok-th.html"}], "maxReviewsPerHotel": 20, "sort": "NEWEST"}` | Agoda $5.40, Trip.com $3.60 / 1,000 |
| Yelp reviews | `arcadium/yelp-reviews` | `{"startUrls": [{"url": "https://www.yelp.com/biz/tartine-bakery-san-francisco-3"}], "maxReviewsPerBusiness": 20, "sort": "DATE_DESC"}` | `review` $0.30 / 1,000 |
| Capterra reviews | `arcadium/capterra-reviews` | `{"startUrls": [{"url": "https://www.capterra.com/p/135003/Slack/reviews/"}], "maxReviewsPerProduct": 20}` | `review` $1.79 / 1,000 |
| Capterra category lists, pricing, features | `arcadium/capterra-products` | `{"startUrls": [{"url": "https://www.capterra.com/project-management-software/"}], "maxResultsPerCategory": 50}` | `result` $6.21 / 1,000 |
| TrustRadius reviews | `arcadium/trustradius-reviews` | `{"startUrls": [{"url": "https://www.trustradius.com/products/asana/reviews"}], "maxReviewsPerProduct": 20}` | `review` $3.59 / 1,000 |
| Software reviews from Capterra, Google Play and App Store in one run | `arcadium/software-reviews` | `{"products": ["Slack"], "sources": ["capterra", "googleplay", "appstore"], "maxReviewsPerSource": 20}` | `review` $1.79 / 1,000 |
| Watch review pages for new negative reviews and rating drift | `arcadium/reputation-monitor` | `{"startUrls": ["https://www.yelp.com/biz/katzs-delicatessen-new-york"], "maxReviewsPerEntity": 50}` | `entity-check` $0.012 each |
| Google Trends interest over time, related queries | `arcadium/google-trends` | `{"searchTerms": ["webscraping"]}` | `result` $2.70 / 1,000 |
| Google News articles with real URLs and full text | `arcadium/google-news` | `{"queries": ["artificial intelligence"], "language": "en", "country": "US", "maxArticlesPerQuery": 20}` | `article` $3.60 / 1,000 |
| YouTube videos from a channel or search | `arcadium/youtube-videos` | `{"searchQueries": ["framework laptop review"], "maxResults": 10}` | `video` $3.60 / 1,000 (`video-listing` $1.17 with `"listingOnly": true`) |
| YouTube transcripts and subtitles | `arcadium/youtube-transcripts` | `{"urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]}` | `transcript` $2.48 / 1,000 |
| Open jobs from company career sites (Workday, Greenhouse, Lever, Ashby, Personio and more) | `arcadium/career-site-jobs` | `{"companies": ["stripe.com", "ashby:openai"], "maxJobsPerCompany": 50}` | `job` $1.80 / 1,000 |
| Which ATS a company uses, open job count | `arcadium/ats-lookup` | `{"companies": ["stripe.com", "notion.so"]}` | `company-lookup` $4.00 / 1,000 |
| Seek jobs (Australia, New Zealand) | `arcadium/seek-jobs` | `{"keywords": ["data analyst"], "locations": ["Sydney NSW"], "maxJobsPerSearch": 50}` | `job` $1.80 / 1,000 |
| AutoScout24 used cars (8 EU countries) | `arcadium/eu-car-listings` | `{"startUrls": ["https://www.autoscout24.de/lst/volkswagen/golf?atype=C&cy=D&fregfrom=2020"], "maxResultsPerSearch": 50}` | `listing` $0.44 / 1,000 |

Each run also has a start fee of $0.001 ($0.00005 for google-trends). Paid Apify plans pay less per result.

## Limits to respect

- Always set the per-source limit (`maxResultsPerSearch`, `maxReviewsPerPlace`, ...). If you leave it out the actor uses its own default (100 reviews per place or business, 1,000 jobs per company for career-site-jobs), which costs more than a first test needs.
- Public data only. The actors do not log in and do not return reviewer names, emails or phone numbers. Do not add personal data from other sources.
- For full field lists and every option, read the actor's input schema (Apify MCP tool `fetch-actor-details`, or the actor page on the Apify Store).
