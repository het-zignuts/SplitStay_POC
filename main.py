from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List

# Add engine directory to import path because folder name has a hyphen.
PROJECT_ROOT = Path(__file__).resolve().parent
ENGINE_DIR = PROJECT_ROOT / "splitstay-engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from filter import is_relevant
from scrapper import get_posts
from sheet import GoogleSheetService
from subreddits import CATEGORY_BY_SUBREDDIT, KEYWORDS, SUBREDDITS
from config import settings


def setup_logging() -> None:
    settings.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(settings.LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def flatten_keywords(keywords_map: dict[str, list[str]]) -> List[str]:
    all_keywords: List[str] = []
    for values in keywords_map.values():
        all_keywords.extend(values)
    return [k.lower() for k in all_keywords]


def load_last_run() -> datetime | None:
    if settings.RUN_MODE == "FULL":
        return None

    if not settings.LAST_RUN_PATH.exists():
        return None

    value = settings.LAST_RUN_PATH.read_text(encoding="utf-8").strip()
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logging.warning("Invalid last_run timestamp in %s; ignoring", settings.LAST_RUN_PATH)
        return None


def save_last_run(run_time: datetime) -> None:
    settings.LAST_RUN_PATH.write_text(run_time.isoformat(), encoding="utf-8")


def iter_subreddits(subreddits_map: dict[str, list[str]]) -> Iterable[tuple[str, str]]:
    for category, names in subreddits_map.items():
        for name in names:
            yield category, name


def main() -> int:
    try:
        settings.validate()
    except Exception as exc:
        print(f"Configuration error: {exc}")
        return 1

    setup_logging()
    run_started_at = datetime.utcnow()
    keyword_list = flatten_keywords(KEYWORDS)

    logging.info("Starting run in %s mode", settings.RUN_MODE)

    try:
        sheet_service = GoogleSheetService(
            credentials_path=settings.GOOGLE_CREDENTIALS_PATH,
            sheet_name=settings.GOOGLE_SHEET_NAME,
            worksheet_name=settings.GOOGLE_WORKSHEET_NAME,
        )
    except Exception as exc:
        logging.exception("Failed to initialize Google Sheet service: %s", exc)
        return 1

    existing_urls = sheet_service.get_existing_urls()
    cutoff = load_last_run()
    if cutoff:
        logging.info("NEW mode cutoff active: %s UTC", cutoff.isoformat())

    rows_to_insert: list[list[str | Any]] = []
    seen_urls = set(existing_urls)

    scanned_posts = 0
    relevant_posts = 0
    skipped_old = 0
    skipped_duplicate = 0
    skipped_keyword = 0

    for default_category, subreddit_name in iter_subreddits(SUBREDDITS):
        logging.info("Fetching r/%s", subreddit_name)
        posts = get_posts(subreddit_name)

        for post in posts:
            scanned_posts += 1

            if cutoff and post["created"] <= cutoff:
                skipped_old += 1
                continue

            url = post.get("url", "")
            if not url or url in seen_urls:
                skipped_duplicate += 1
                continue

            match, matched_keywords = is_relevant(post, keyword_list)
            if not match:
                skipped_keyword += 1
                continue

            relevant_posts += 1
            seen_urls.add(url)
            category = CATEGORY_BY_SUBREDDIT.get(subreddit_name.lower(), default_category)
            rows_to_insert.append(sheet_service.format_row(post, matched_keywords, category))

    sheet_service.append_rows(rows_to_insert)
    save_last_run(run_started_at)

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
