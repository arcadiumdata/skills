# n8n workflows

Importable n8n workflows that call Arcadium Data scrapers on Apify and write the results to Google Sheets (and Slack where noted).

| Workflow | What it does | Guide |
| --- | --- | --- |
| `n8n-trustpilot-new-reviews-to-sheets-and-slack.json` | Only new Trustpilot reviews to a Sheet, with a Slack line for low-star reviews | https://scrapers.arcadiumdata.io |
| `n8n-trustpilot-competitors-to-google-sheets.json` | Trustpilot reviews for several companies in one Sheet | https://scrapers.arcadiumdata.io |
| `n8n-youtube-transcripts-to-google-sheets.json` | YouTube transcripts with timestamps to a Sheet | https://scrapers.arcadiumdata.io |
| `n8n-google-trends-interest-over-time-to-google-sheets.json` | Google Trends interest over time to a Sheet | https://scrapers.arcadiumdata.io |
| `n8n-google-trends-compare-to-google-sheets.json` | Compare Google Trends keywords in a Sheet | https://scrapers.arcadiumdata.io |
| `n8n-amazon-aliexpress-search-to-google-sheets.json` | Amazon and AliExpress search results side by side | https://scrapers.arcadiumdata.io |

Import: n8n > Workflows > Import from file. Replace `APIFY_CREDENTIAL_ID` with your own Apify credential and pick your Google Sheets / Slack credentials. No keys are stored in these files.
