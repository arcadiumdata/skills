---
name: hiring-signals
description: Turn company domains into hiring signals - which ATS each company uses (Greenhouse, Lever, Ashby, Workday, Personio, Workable, Recruitee, Teamtailor, SmartRecruiters), how many jobs are open, jobs posted in the last 30 days, department and country mix, remote and posted-pay share - then pull the open jobs themselves and watch for new ones. Use when the user wants account research, buying or expansion signals, which target accounts are hiring for a role, competitor hiring analysis, or a weekly new-jobs feed from company career sites. Runs Arcadium Data actors on Apify with the user's own APIFY_TOKEN (pay per company found or job).
license: MIT
metadata:
  author: Arcadium Data
  author_url: https://arcadiumdata.io
  category: sales
  keywords: "hiring signals, job postings, careers page, ats detection, greenhouse, lever, workday, personio, account research, buying signals, sales prospecting, competitor hiring"
  apify-actors: "arcadium/ats-lookup, arcadium/career-site-jobs"
---

# Hiring signals from company career sites

Two steps: a cheap scan of a company list (which ATS, how many jobs, how fast they post, in which teams and countries), then the actual jobs for the companies that matter, with an optional weekly "new jobs only" watch.

**Disclosure:** the actors this skill runs are built and sold by Arcadium Data, the author of this skill. You pay Apify per company found or per job (see Cost). No affiliate codes are used.

## Example prompts

- "Which of these 40 SaaS companies are hiring sales people in Germany right now?"
- "Is stripe.com growing its engineering team? Show department mix and jobs posted in the last 30 days."
- "Set up a weekly list of new data engineering jobs at my target accounts."

Out of scope:

- Job boards (Indeed, LinkedIn, Glassdoor): these actors read the company's own career site only.
- People: no recruiter or hiring manager names are returned, and emails and phone numbers in job descriptions are masked. Do not look up or add contacts from other sources in this skill.

## Prerequisites

- Apify account and `APIFY_TOKEN`, or `apify login`. Apify CLI (`npm i -g apify-cli`) or the Apify MCP server (`https://mcp.apify.com`).

## Cost

Free Apify plan prices; paid plans pay less. Companies with no job board found, closed-job rows, coverage and error rows are free.

| Actor | Charged event | Free plan | Start fee per run |
| --- | --- | --- | --- |
| `arcadium/ats-lookup` | `company-lookup` | $4.00 per 1,000 | $0.001 |
| `arcadium/career-site-jobs` | `job` | $1.80 per 1,000 | $0.001 |
| `arcadium/career-site-jobs` | `company` | $1.80 per 1,000 | $0.001 |

`company-lookup` is charged only for a company whose public job board was found. `company` is charged per company checked in only-changes (monitoring) mode; unchanged jobs are not charged again.

Worked example: scan 40 domains (at most 40 x $0.004 + $0.001 = $0.161), then pull up to 50 jobs each for the 8 most active (400 x $0.0018 + $0.001 = $0.721): **about $0.88 at most**. A weekly watch of the same 8 companies costs 8 x $0.0018 = $0.0144 plus $0.0018 per new job and the $0.001 start fee.

## Workflow

### 1. Scan the company list

<!-- input: ats-lookup -->
```json
{
  "companies": ["stripe.com", "notion.so", "https://jobs.lever.co/zoox", "ashby:openai"]
}
```

    apify actors call arcadium/ats-lookup --input-file companies.json --user-agent arcadium-skills/hiring-signals --json 2>/dev/null
    apify datasets get-items DATASET_ID --format json --user-agent arcadium-skills/hiring-signals 2>/dev/null > ats-items.json

(`DATASET_ID` is `.defaultDatasetId` from the call output.) Inputs can be domains, career-page or job-board links, or `ats:token` pairs. Per company: `ats`, `boardUrl`, `matchConfidence`, `openJobs` (with `openJobsIsLowerBound`), `sampledJobs`, `departmentMix` and `countryMix` (`jobs`, `share`), `remoteShare`, `payShare` and `pay` (per currency `low`, `high`, `medianMid`), `newestPostedAt`, `jobsPostedLast30Days`, `dataAsOf`.

Rank and explain:

- **Velocity:** `jobsPostedLast30Days` and its share of `openJobs` (a high share = a hiring push now).
- **Focus:** the top 3 departments in `departmentMix` (for example Sales or Customer Success growth = go-to-market push; Data or ML = new capability).
- **Footprint:** countries in `countryMix`; on a re-run, a new country = expansion signal.
- **Pay transparency:** `payShare`, and posted pay bands where present.

Companies with no board come back as free rows; say which ones and do not guess their hiring.

### 2. Pull the jobs that matter

<!-- input: career-site-jobs -->
```json
{
  "companies": ["stripe.com", "notion.so"],
  "keywords": ["account executive", "sales"],
  "countries": ["DE"],
  "postedWithinDays": 30,
  "maxJobsPerCompany": 50,
  "includeDescriptions": "text",
  "maxDescriptionChars": 2000
}
```

    apify actors call arcadium/career-site-jobs --input-file jobs.json --user-agent arcadium-skills/hiring-signals --json 2>/dev/null

Job rows (`rowType: "job"`): `company`, `ats`, `title`, `department`, `team`, `locations`, `countries`, `remote`, `employmentType`, `seniority`, `salary`, `postedAt`, `updatedAt`, `url`, `applyUrl`, `description`. Leave `keywords` and `countries` out for every job; set `includeDescriptions: "none"` when only titles and counts are needed.

### 3. Optional: weekly watch

Run the same input with `"onlyChanges": true` and a fixed `"stateKey"` (for example `"target-accounts"`), on an Apify schedule or by hand. The first run is the baseline; later runs return only new jobs plus a free `closed` row for each job that disappeared. Report new and closed counts per company.

## MCP instead of the CLI

With the Apify MCP server connected, call `arcadium/ats-lookup` and `arcadium/career-site-jobs` with the same inputs.

## Troubleshooting

- A domain with no board found: try the careers page link instead of the bare domain, or the `ats:token` form if the board URL is known (`greenhouse:stripe`).
- `coverage` rows with `shortfall` mean `maxJobsPerCompany` or filters cut the list; raise the cap if the counts matter.
- `error` rows `blocked` / `unavailable`: retry later; other companies in the run are still delivered.
