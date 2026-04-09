from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


class Settings:
    """Pipeline configuration"""

    BASE_DIR = Path(__file__).resolve().parent

    # Reddit API
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT")

    # Google Sheets
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME")
    GOOGLE_CREDENTIALS_PATH: str = str(
        (BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")).resolve()
    )

    GOOGLE_WORKSHEET_NAME: str = os.getenv("GOOGLE_WORKSHEET_NAME", "Sheet1")

    # Run settings
    RUN_MODE: str = os.getenv("RUN_MODE", "NEW").upper()
    POST_LIMIT: int = int(os.getenv("POST_LIMIT", "100"))

    # Paths
    LAST_RUN_PATH: Path = BASE_DIR / "last_run.txt"
    LOG_PATH: Path = BASE_DIR / "run.log"

    # ---- Optional Validation (lightweight) ----
    if RUN_MODE not in {"FULL", "NEW"}:
        raise ValueError("RUN_MODE must be FULL or NEW")

    if POST_LIMIT <= 0:
        raise ValueError("POST_LIMIT must be > 0")

    REQUIRED_VARS = {
        "REDDIT_CLIENT_ID": REDDIT_CLIENT_ID,
        "REDDIT_CLIENT_SECRET": REDDIT_CLIENT_SECRET,
        "REDDIT_USER_AGENT": REDDIT_USER_AGENT,
        "GOOGLE_SHEET_NAME": GOOGLE_SHEET_NAME,
        "GOOGLE_CREDENTIALS_PATH": GOOGLE_CREDENTIALS_PATH,
    }

    missing = [k for k, v in REQUIRED_VARS.items() if not v or not str(v).strip()]
    if missing:
        raise ValueError(f"Missing env vars: {', '.join(missing)}")

    
settings = Settings()
