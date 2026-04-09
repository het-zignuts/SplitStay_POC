"""
Expected Sheet Columns:
[Post Title, Subreddit, Author, Post URL, Post Date, Detected At, Keywords Matched, Event Detected, Location, Category, Lead Score, Status]
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging


class GoogleSheetService:
    """
    Service class for interacting with Google Sheets.

    Responsibilities:
    - Authenticate using service account
    - Fetch existing URLs for deduplication
    - Append processed rows
    """

    def __init__(self, credentials_path: str, sheet_name: str):
        """
        Initialize Google Sheets client.

        Args:
            credentials_path (str): Path to credentials.json file
            sheet_name (str): Name of the Google Sheet
        """

        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path,
            self.scope
        )

        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open(sheet_name).sheet1

        logging.info("Connected to Google Sheet")

    def get_existing_urls(self) -> set:
        """
        Fetch all existing Post URLs from the sheet (Column D).

        Returns:
            set: Set of existing URLs
        """

        try:
            urls = self.sheet.col_values(4)
            return set(urls[1:])
        except Exception as e:
            logging.error(f"Failed to fetch existing URLs: {e}")
            return set()

    def format_row(self, post: dict, keywords: list, category: str) -> list:
        """
        Convert Reddit post + metadata into sheet row format.

        Args:
            post (dict): Reddit post payload
            keywords (list): Matched keywords
            category (str): Derived category

        Returns:
            list: Row formatted for Google Sheet
        """

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

    def is_duplicate(self, post_url: str) -> bool:
        """
        Check if given Post URL already exists in Google Sheet.

        Args:
            post_url (str): Reddit post URL

        Returns:
            bool: True if duplicate, False otherwise
        """

        try:
            urls = self.sheet.col_values(4)
            
            for url in urls[1:]:
                if url.strip() == post_url.strip():
                    return True

            return False

        except Exception as e:
            logging.error(f"Dedup check failed: {e}")
            return False

    def append_rows(self, rows: list):
        """
        Append multiple rows to the Google Sheet.

        Args:
            rows (list): List of row lists
        """

        if not rows:
            logging.warning("No rows to insert")
            return

        try:
            self.sheet.append_rows(rows, value_input_option="RAW")
            logging.info(f"Inserted {len(rows)} rows into sheet")
        except Exception as e:
            logging.error(f"Failed to append rows: {e}")
