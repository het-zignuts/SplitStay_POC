"""Load environment-driven settings for the Reddit-to-Sheets pipeline."""

from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# Keep configuration local to the engine package directory.
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Expose validated configuration values derived from environment variables."""

    BASE_DIR = BASE_DIR

    # Reddit public JSON API
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "SplitStayBot/1.0")
    REDDIT_REQUEST_TIMEOUT: int = int(os.getenv("REDDIT_REQUEST_TIMEOUT", "20"))
    REDDIT_URL1: str = os.getenv("REDDIT_URL1", "https://www.reddit.com")
    REDDIT_URL2: str = os.getenv("REDDIT_URL2", "https://old.reddit.com")

    # Google Sheets
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME")
    GOOGLE_CREDENTIALS_PATH: str = str(
        (BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")).resolve()
    )
    GOOGLE_WORKSHEET_NAME: str = os.getenv("GOOGLE_WORKSHEET_NAME", "Sheet1")

    # Run settings
    RUN_MODE: str = os.getenv("RUN_MODE", "NEW").upper()
    POST_LIMIT: int = int(os.getenv("POST_LIMIT", "100"))
    LAST_RUN_PATH: Path = BASE_DIR / "last_run.txt"  # Stores last run timestamp (NEW mode only)

    LOG_PATH: Path = BASE_DIR / "run.log"

    def validate(self) -> None:
        """Raise a descriptive error when required settings are missing or invalid."""
        if self.RUN_MODE not in {"FULL", "NEW"}: # checks that the run mode is either FULL or NEW, otherwise raises an error
            raise ValueError("RUN_MODE must be FULL or NEW")

        if self.POST_LIMIT <= 0: # checks that the post limit is a positive integer, otherwise raises an error
            raise ValueError("POST_LIMIT must be > 0")

        if self.REDDIT_REQUEST_TIMEOUT <= 0: # checks that the Reddit request timeout is a positive integer, otherwise raises an error
            raise ValueError("REDDIT_REQUEST_TIMEOUT must be > 0")

        # Validate presence of critical configuration values to avoid runtime errors later on.
        required_vars = {
            "REDDIT_USER_AGENT": self.REDDIT_USER_AGENT,
            "GOOGLE_SHEET_NAME": self.GOOGLE_SHEET_NAME,
            "GOOGLE_CREDENTIALS_PATH": self.GOOGLE_CREDENTIALS_PATH,
        }

        # List out missing or empty required variables for easier debugging.
        missing = [k for k, v in required_vars.items() if not v or not str(v).strip()]
        if missing:
            raise ValueError(f"Missing env vars: {', '.join(missing)}")


settings = Settings()