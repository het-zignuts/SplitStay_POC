from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

# Add engine directory to import path because folder name has a hyphen.
PROJECT_ROOT = Path(__file__).resolve().parent
ENGINE_DIR = PROJECT_ROOT / "splitstay-engine"

if str(ENGINE_DIR) not in sys.path: 
    sys.path.insert(0, str(ENGINE_DIR))

# Adding the necessary imports
from filter import is_relevant
from scrapper import get_posts
from sheet import GoogleSheetService
from subreddits import ALL_KEYWORDS, KEYWORD_GROUPS, SUBREDDITS
from config import settings

def setup_logging() -> None:
    """Configure file and console logging for the current run."""
    settings.LOG_PATH.parent.mkdir(parents=True, exist_ok=True) # Ensure the log directory exists before configuring logging 
    
    # Configure logging to write to a file and also output to the console with timestamps and log levels for better traceability.
    logging.basicConfig( 
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(settings.LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
def load_last_run() -> datetime | None:
    """Load the previous run timestamp when operating in incremental mode."""
    if settings.RUN_MODE == "FULL": # In FULL mode, we do not use a cutoff timestamp, so we return None to indicate that all posts should be considered regardless of creation time.
        return None

    # If the last run file does not exist or is empty, return None to indicate that there is no cutoff and all posts should be considered. 
    if not settings.LAST_RUN_PATH.exists():
        return None

    # Read the last run timestamp from the file, stripping any whitespace. If the file is empty, return None to indicate no cutoff.
    value = settings.LAST_RUN_PATH.read_text(encoding="utf-8").strip()
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logging.warning("Invalid last_run timestamp in %s; ignoring", settings.LAST_RUN_PATH)
        return None


def save_last_run(run_time: datetime) -> None:
    """Persist the timestamp used as the next incremental-run cutoff."""

    # Write the current run timestamp to the last run file in ISO format, which will be used as a cutoff for the next run in NEW mode
    settings.LAST_RUN_PATH.write_text(run_time.isoformat(), encoding="utf-8")


def iter_subreddits(subreddits_map: dict[str, list[str]]) -> Iterable[tuple[str, str]]:
    """Yield category and subreddit pairs from the configured mapping."""

    # Iterate through the subreddits map, yielding each category and subreddit name pair for processing. 
    for category, names in subreddits_map.items():
        for name in names:
            yield category, name


def main() -> int:
    """Fetch relevant subreddit posts and append unseen matches to Google Sheets."""
    try:
        settings.validate() # validate the configuration settings at the start of the main function to catch any issues early and prevent runtime errors later on in the execution.
    except Exception as exc:
        print(f"Configuration error: {exc}")
        return 1

    setup_logging() # Set up logging for the current run.
    run_started_at = datetime.utcnow()

    logging.info("Starting run in %s mode", settings.RUN_MODE)

    try:
        # Initialize the Google Sheet service with the provided credentials and sheet information
        sheet_service = GoogleSheetService(
            credentials_path=settings.GOOGLE_CREDENTIALS_PATH,
            sheet_name=settings.GOOGLE_SHEET_NAME,
            worksheet_name=settings.GOOGLE_WORKSHEET_NAME,
        )
    except Exception as exc:
        logging.exception("Failed to initialize Google Sheet service: %s", exc)
        return 1

    existing_urls = sheet_service.get_existing_urls() # Fetch existing URLs from the Google Sheet
    cutoff = load_last_run() # Load the last run timestamp to use as a cutoff for filtering posts in NEW mode. 
    if cutoff:
        logging.info("NEW mode cutoff active: %s UTC", cutoff.isoformat())

    # Track rows to append in one batch and avoid reprocessing URLs already stored.
    rows_to_insert: list[list[str | Any]] = []
    seen_urls = set(existing_urls)

    scanned_posts = 0
    relevant_posts = 0
    skipped_old = 0
    skipped_duplicate = 0
    skipped_keyword = 0

    for default_category, subreddit_name in iter_subreddits(SUBREDDITS):
        logging.info("Fetching r/%s", subreddit_name)
        
        # Fetch posts from the subreddit using the get_posts function, which retrieves recent posts from the specified subreddit and returns them as a list of dictionaries containing post data.
        posts = get_posts(subreddit_name) 

        for post in posts:
            scanned_posts += 1

            # In NEW mode, ignore posts that were already available on the last run.
            if cutoff and post["created"] <= cutoff:
                skipped_old += 1
                continue

            url = post.get("url", "")
            # Skip empty URLs and anything already present in the sheet or this run.
            if not url or url in seen_urls:
                skipped_duplicate += 1
                continue
            # to-do: adding title-based deduplication

            # Use both explicit phrase keywords and grouped word-pattern matches.
            match, matched_keywords = is_relevant(post, ALL_KEYWORDS, KEYWORD_GROUPS)
            # Only keep posts that match the configured keyword set.
            if not match:
                skipped_keyword += 1
                continue

            relevant_posts += 1
            seen_urls.add(url) # Add the URL to the seen set to prevent duplicates within the same run.
            rows_to_insert.append(sheet_service.format_row(post, matched_keywords, default_category)) # Format the post data into a row format suitable for insertion into the Google Sheet

    # Append the rows to the Google Sheet
    sheet_service.append_rows(rows_to_insert)
    save_last_run(run_started_at) # Save the current run timestamp to be used as a cutoff for the next run in NEW mode

    logging.info(
        "Run complete | scanned=%d relevant=%d inserted=%d skipped_old=%d skipped_duplicate=%d skipped_keyword=%d",
        scanned_posts,
        relevant_posts,
        len(rows_to_insert),
        skipped_old,
        skipped_duplicate,
        skipped_keyword,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
