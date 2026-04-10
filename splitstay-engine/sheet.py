"""
Google Sheets integration used for deduplication and row insertion.

Expected sheet columns:
[Post Title, Subreddit, Author, Post URL, Post Date, Detected At, Keywords Matched, Event Detected, Location, Category, Lead Score, Status]
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging

EXPECTED_COLUMNS = [
    "Post Title",
    "Subreddit",
    "Author",
    "Post URL",
    "Post Date",
    "Detected At",
    "Keywords Matched",
    "Event Detected",
    "Location",
    "Category",
    "Lead Score",
    "Status"
]


class GoogleSheetService:
    """Wrap the Google Sheets client used by the ingestion pipeline."""

    def __init__(self, credentials_path: str, sheet_name: str, worksheet_name: str = "Sheet1"):
        """Authenticate and bind the service to the target worksheet."""

        # The scope defines the permissions the service account needs to access Google Sheets and Drive.
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        # Authenticate using the service account credentials JSON file and authorize the gspread client.
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path,
            self.scope
        )

        self.client = gspread.authorize(self.creds)  # create a client to interact with Google Sheets
        workbook = self.client.open(sheet_name)
        self.sheet = workbook.worksheet(worksheet_name)
        self.ensure_headers()

        logging.info("Connected to Google Sheet: %s / %s", sheet_name, worksheet_name)

    def ensure_headers(self) -> None:
        """Ensure the worksheet starts with the expected header row."""
        try:
            current_headers = self.sheet.row_values(1)
            if current_headers[: len(EXPECTED_COLUMNS)] == EXPECTED_COLUMNS:
                return

            self.sheet.update("A1:L1", [EXPECTED_COLUMNS])
            logging.info("Sheet headers initialized or refreshed")
        except Exception as e:
            logging.error(f"Failed to ensure sheet headers: {e}")

    def get_existing_urls(self) -> set:
        """Return the set of post URLs already stored in column D."""

        try:
            urls = self.sheet.col_values(4)
            # Skip the header row so only previously inserted URLs are tracked.
            return set(urls[1:])
        except Exception as e:
            logging.error(f"Failed to fetch existing URLs: {e}")
            return set()

    def format_row(self, post: dict, keywords: list, category: str) -> list:
        """Convert a normalized post and its metadata into the expected row format."""

        detected_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        post_date = post["created"].strftime("%Y-%m-%d %H:%M:%S")

        return [
            post.get("title", ""),
            post.get("subreddit", ""),
            post.get("author", ""),
            post.get("url", ""),
            post_date,
            detected_at,
            ", ".join(keywords) if keywords else "",
            "",
            "",
            category,
            "",
            "New"
        ]

    def append_rows(self, rows: list):
        """Append a batch of rows to the sheet when new matches exist."""

        if not rows:
            logging.warning("No rows to insert")
            return

        try:
            # Append the rows to the sheet with RAW input option to preserve formatting and avoid formula injection.
            self.sheet.append_rows(rows, value_input_option="RAW", table_range="A1")
            logging.info(f"Inserted {len(rows)} rows into sheet")
        except Exception as e:
            logging.error(f"Failed to append rows: {e}")
