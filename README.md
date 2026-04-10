# SplitStay POC

SplitStay scans selected subreddits, finds posts related to sharing accommodation/travel costs, and writes matched posts to Google Sheets.

It uses Reddit public JSON endpoints (`.json`) and does not require Reddit OAuth client ID/secret for fetching posts.

## How It Works

1. Fetch latest posts from configured subreddits.
2. Normalize text and match against configured keywords.
3. Skip duplicates already present in the sheet (based on Post URL).
4. Append matched rows to Google Sheet.
5. Save run timestamp in `last_run.txt` (used in `NEW` mode).

## Project Structure

```text
main.py
splitstay-engine/
  config.py        # env + settings validation
  scrapper.py      # Reddit JSON fetcher
  filter.py        # keyword matching logic
  sheet.py         # Google Sheets read/append
  subreddits.py    # subreddit + keyword configuration
  credentials.json # Google service account key
  .env             # runtime configuration
  run.log          # file logs
  last_run.txt     # last run timestamp (NEW mode)
```

## Requirements

- Python 3.10+
- A Google Cloud service account JSON key with Sheets/Drive access
- Target Google Sheet shared with the service account email

Install dependencies:

```bash
pip install -r splitstay-engine/requirements.txt
```

## Environment Variables

Create/update `splitstay-engine/.env`:

```env
REDDIT_USER_AGENT=Mozilla/5.0 ...
REDDIT_REQUEST_TIMEOUT=10

GOOGLE_SHEET_NAME=SplitStay-Data
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_WORKSHEET_NAME=Sheet1

RUN_MODE=FULL
POST_LIMIT=50
```

Notes:
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` are not used by current JSON flow.
- `GOOGLE_CREDENTIALS_PATH` is resolved relative to `splitstay-engine/`.
- `RUN_MODE`:
  - `FULL`: no date cutoff, scans all fetched posts.
  - `NEW`: only considers posts newer than `last_run.txt`.

## Google Sheet Columns

The pipeline writes rows in this order:

1. Post Title
2. Subreddit
3. Author
4. Post URL
5. Post Date
6. Detected At
7. Keywords Matched
8. Event Detected
9. Location
10. Category
11. Lead Score
12. Status

## Run

From project root:

```bash
python main.py
```

## Logging and Run State

- Terminal logs are printed during execution.
- File logs are written to: `splitstay-engine/run.log`
- Last run checkpoint (for `NEW` mode): `splitstay-engine/last_run.txt`
