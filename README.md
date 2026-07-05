# Instagram Analytics Tool

Offline Instagram export analytics with both a command line interface and a
local upload dashboard.

The project is designed to replace one-off Instagram Python experiments with a
clean, reproducible tool. It does not use hardcoded usernames, local absolute
paths, cookies, session IDs, webhooks, or API tokens.

## What It Does

- Reads Instagram export JSON files or folders.
- Extracts interaction records from common export sections, including post likes,
  story likes, story interactions, and comments.
- Extracts saved post metrics from JSON documents that contain `like_count` and
  `comment_count` fields.
- Produces top-account rankings, interaction type counts, date ranges, monthly
  trend data, and post engagement averages.
- Generates Markdown reports and SVG charts.
- Provides a local browser UI where a user can upload JSON files and see the
  stats immediately.

## What It Does Not Do

- It does not scrape Instagram.
- It does not log in to Instagram.
- It does not store or require cookies, `sessionid`, `fb_dtsg`, usernames, API
  keys, webhooks, or local machine paths.

## Setup

Use Python 3.10 or newer.

```bash
cd instagram-analytics-tool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The runtime uses only the Python standard library.

## CLI Usage

Analyze a file or folder and print JSON:

```bash
instagram-analytics analyze examples/sample_export.json
```

Write a Markdown report:

```bash
instagram-analytics report examples/sample_export.json -o output/report.md
```

Write SVG charts:

```bash
instagram-analytics charts examples/sample_export.json -o output
```

Start the local upload UI:

```bash
instagram-analytics web
```

Then open:

```text
http://127.0.0.1:8088
```

You can also run without installing:

```bash
PYTHONPATH=src python -m instagram_analytics.cli web
```

## UI Usage

1. Export your Instagram data from Instagram's account data download tools.
2. Start the UI with `instagram-analytics web`.
3. Open the local URL.
4. Upload one or more `.json` files from your export.
5. View summary stats, top accounts, monthly trend charts, and the generated
   Markdown report.

The UI runs locally. It does not upload data to any external service.

## Data Sources

Recommended inputs:

- `your_instagram_activity/likes/liked_posts.json`
- `your_instagram_activity/story_sticker_interactions/story_likes.json`
- other official Instagram export `.json` files

The extractor is intentionally tolerant: it walks JSON documents and looks for
known Instagram export keys and common post metric fields.

## Development

Run tests with the standard library test runner:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Run a quick syntax check:

```bash
python -m compileall src tests
```

## Migrating The Old Scripts

Use this mapping:

- `likedposts.py` -> official export loading, account counting, bar charts.
- `instagram_analyser.py` and `insta-analyse2.py` -> post metric trend analysis
  from saved JSON data.
- `import requests.py`, `reqinsat.py`, `rmh.py`, `tewss.py`, `testr.py`,
  `inp.py`, and `instachat make.py` -> do not migrate directly. They depended
  on cookies, sessions, hardcoded usernames, or private endpoints. Keep that
  behavior out of this project.

## Repository Safety

The `.gitignore` excludes likely personal export directories and generated
outputs. Do not commit real Instagram exports unless you deliberately create an
anonymized fixture.
