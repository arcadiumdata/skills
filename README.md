# Arcadium Data Agent Skills

Open-source [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) (`SKILL.md` folders) for review mining, product research, YouTube research, hotel reputation and hiring signals. Each skill tells a coding or research agent (Claude Code, Codex, Cursor, Gemini CLI and others that read `SKILL.md`) which Apify actor to run, with which input, what the output fields mean and what the run costs.

**Disclosure.** Arcadium Data built and sells every actor these skills route to (Apify Store user `arcadium`). The actors are pay-per-event: you pay Apify per result with your own Apify account, at the prices listed in each skill. The skills themselves are free (MIT). No affiliate or referral codes are used in any link.

## Install

```bash
# all skills
npx skills add arcadiumdata/skills

# one skill
npx skills add arcadiumdata/skills --skill competitor-review-mining
```

Or copy a skill folder into `~/.claude/skills/` (Claude Code) or your agent's skills directory.

## Requirements

- An Apify account and an API token (`APIFY_TOKEN`), from [Apify Console > Settings > Integrations](https://console.apify.com/settings/integrations).
- One way to call actors:
  - the [Apify CLI](https://docs.apify.com/cli) (`npm i -g apify-cli`, then `apify login` or `APIFY_TOKEN` in the environment), or
  - the hosted Apify MCP server at `https://mcp.apify.com` ([docs](https://docs.apify.com/platform/integrations/mcp)), or
  - the Apify REST API (`POST https://api.apify.com/v2/acts/arcadium~<actor>/run-sync-get-dataset-items`).
- Python 3.9+ only for the two skills that ship a small helper script (standard library only).

## Skills

| Skill | What it produces | Actors |
| --- | --- | --- |
| [competitor-review-mining](skills/competitor-review-mining/SKILL.md) | Low-star reviews of competitors from Capterra, TrustRadius, Google Play and the App Store, saved in the `competitor-profiles/raw/<slug>/<date>/reviews/` layout that the marketingskills `competitor-profiling` skill reads, plus a ranked complaint list | `arcadium/capterra-reviews`, `arcadium/trustradius-reviews`, `arcadium/software-reviews` |
| [replica-reviews-csv](skills/replica-reviews-csv/SKILL.md) | `reviews.csv` with `source,url,date,rating,text` from 3 or more review sites, recent and low-rated first | `arcadium/capterra-reviews`, `arcadium/trustradius-reviews`, `arcadium/software-reviews` |
| [amazon-product-opportunity](skills/amazon-product-opportunity/SKILL.md) | Google Trends demand, Amazon competition and 1688 factory prices for a product idea; a drop-in for the Google Trends and supplier steps of product research skills | `arcadium/google-trends`, `arcadium/amazon-products`, `arcadium/1688-products` |
| [youtube-transcript-research](skills/youtube-transcript-research/SKILL.md) | Find videos on a topic, pull their transcripts, and summarise claims with timestamps | `arcadium/youtube-videos`, `arcadium/youtube-transcripts` |
| [hotel-reputation-audit](skills/hotel-reputation-audit/SKILL.md) | One hotel (or a hotel and its competitors) across Tripadvisor, Booking.com, Google Hotels, Agoda and Trip.com on one 1-5 scale, with complaint themes and reply rate | `arcadium/hotel-reputation`, `arcadium/tripadvisor-reviews`, `arcadium/booking-reviews`, `arcadium/google-hotel-reviews` |
| [hiring-signals](skills/hiring-signals/SKILL.md) | Which ATS a company uses, how many jobs are open, which teams and countries are hiring, and the open jobs themselves | `arcadium/ats-lookup`, `arcadium/career-site-jobs` |
| [arcadium-web-data](skills/arcadium-web-data/SKILL.md) | A router: from a data request (Amazon, Etsy, 1688, hotel prices and reviews, Yelp, Capterra, TrustRadius, app reviews, Google Trends, Google News, YouTube, career-site jobs, Seek, ATS, AutoScout24) to the actor ID, a first input that works and the price | all 24 public `arcadium/*` actors |

### competitor-review-mining

"Mine 1 and 2 star reviews for Asana, Monday.com and ClickUp and rank the complaints." Capterra and TrustRadius filter by rating on the site; Google Play and App Store reviews are filtered by the helper script `scripts/split_reviews.py`, which writes `competitor-profiles/raw/<slug>/<YYYY-MM-DD>/reviews/<platform>.json` and `.md`. About $0.90 at most for one competitor at 100 reviews per site. Trustpilot is added once Arcadium's Trustpilot actor is public.

### replica-reviews-csv

"Build replica/reviews.csv for Todoist." Writes `source,url,date,rating,text` with source names `capterra`, `trustradius`, `google-play`, `app-store`, low-rated rows first, through `scripts/to_reviews_csv.py`. About $0.45 at most for 200 reviews. This is a data source the user chooses to run; replica-entrepreneur itself asks for reviews collected by reading, and its author does not endorse this skill.

### amazon-product-opportunity

"Is a yoga mat a good product to sell on Amazon US?" Five years of Google Trends interest and rising queries, the Amazon search page (median price, rating counts, sponsored share, bought in past month) and 1688 factory prices at MOQ, then demand, competition and margin scores. About $0.12 per product idea. Replaces the `web_fetch` Google Trends step in product-research skills.

### youtube-transcript-research

"What do the top YouTube reviews of the Framework Laptop 13 complain about?" Search in fast listing mode, then transcripts with timed segments, so every claim links to `<url>&t=<start>s`. About $0.07 for 30 search results and 15 transcripts.

### hotel-reputation-audit

"Audit the online reputation of The Savoy in London." One run across Tripadvisor, Booking.com, Google Hotels (and Agoda, Trip.com) with ratings on one 1-5 scale and a combined summary row (about $1.35 for 300 reviews), or one actor per site for about $0.69 for the same 300 reviews.

### hiring-signals

"Which of these 40 SaaS companies are hiring sales people in Germany?" ATS detection with open jobs, 30-day velocity, department and country mix for a company list (charged only when a board is found), then the matching jobs and an optional weekly new-jobs watch. About $0.88 at most for 40 companies scanned and 400 jobs.

## Data rules

- Public data only. The actors do not log in and do not return reviewer names, emails or phone numbers; job rows carry no recruiter names and mask contact details in descriptions. The skills never ask the agent to add personal data from other sources.
- Every skill states the free-plan price per result and the start fee. Paid Apify plans pay less per result.
- Free rows (`error`, `coverage`, `summary`) are never charged. Filter on `rowType`.

## CLI conventions

Every CLI command in these skills uses `--json` (or `--format json`), `2>/dev/null` and `--user-agent arcadium-skills/<skill-name>`, the same pattern as [apify/awesome-skills](https://github.com/apify/awesome-skills).

## Links

- Actors on the Apify Store: <https://apify.com/arcadium>
- Arcadium Data: <https://arcadiumdata.io>
- Issues and new skill ideas: open an issue in this repo.

## License

MIT, see [LICENSE](LICENSE).
