from __future__ import annotations

"""Fetch recent Reddit posts through the public JSON endpoints."""

from datetime import datetime
import logging
import time
from typing import Any

import requests

from config import settings

BASE_REDDIT_URL = settings.REDDIT_URL1 # base url
FALLBACK_REDDIT_URL = settings.REDDIT_URL2 # fallbcack url for reliability
POST_LIMIT = int(settings.POST_LIMIT) # number of posts to fetch per subreddit


def _normalize_url(permalink: str | None) -> str:
    """Convert Reddit permalinks into absolute URLs."""
    if not permalink: # if the permalink is None or empty, return an empty string to avoid errors in URL construction
        return ""

    if permalink.startswith("http://") or permalink.startswith("https://"): # if the permalink already starts with http:// or https://, it is considered a complete URL and returned as is
        return permalink

    return f"{BASE_REDDIT_URL}{permalink}" # if the permalink does not start with http:// or https://, it is treated as a relative path and the base Reddit URL is prepended to construct the full URL


def _parse_post(child: dict[str, Any], subreddit_name: str) -> dict[str, Any]:
    """Extract the fields used by the pipeline from a Reddit listing item."""

    # The Reddit JSON structure nests post data under a "data" key within each child item, so we access it here for easier field extraction.
    data = child.get("data", {})

    # extracted created_utc timestamp.
    created_utc = data.get("created_utc")
    try:
        created = datetime.utcfromtimestamp(float(created_utc))
    except Exception:
        created = datetime.utcnow()

    # return a normalized dictionary containing the relevant post fields, ensuring that missing values are handled gracefully with defaults.
    return {
        "title": data.get("title") or "",
        "body": data.get("selftext") or "",
        "url": _normalize_url(data.get("permalink")) or data.get("url") or "",
        "author": data.get("author") or "",
        "subreddit": data.get("subreddit") or subreddit_name,
        "created": created,
    }


def get_posts(subreddit_name: str) -> list[dict[str, Any]]:
    """Fetch recent posts for a subreddit, falling back between Reddit domains."""
    posts: list[dict[str, Any]] = []

    # Try both current and old Reddit JSON endpoints to improve reliability.
    endpoints = [
        f"{BASE_REDDIT_URL}/r/{subreddit_name}/new.json",
        f"{FALLBACK_REDDIT_URL}/r/{subreddit_name}/new.json",
    ]

    # Set a custom User-Agent to avoid being blocked by Reddit's API, and specify that we want JSON responses. 
    # #The timeout is configured to prevent hanging on slow responses.
    headers = {
        "User-Agent": settings.REDDIT_USER_AGENT,
        "Accept": "application/json",
    }

    # The Reddit JSON API supports a "limit" parameter to specify how many posts to return, 
    # and "raw_json=1" ensures we get unescaped content for easier processing.
    params = {
        "limit": POST_LIMIT,
        "raw_json": 1,
    }

    try:
        payload: dict[str, Any] | None = None
        last_error: Exception | None = None

        for endpoint in endpoints:
            try:
                # Try both current and old Reddit JSON endpoints to improve reliability.
                response = requests.get(
                    endpoint,
                    headers=headers,
                    params=params,
                    timeout=settings.REDDIT_REQUEST_TIMEOUT,
                )
                
                response.raise_for_status() # error handling
                payload = response.json() # parse the JSON response into a Python dictionary for further processing
                break
            except requests.RequestException as exc:
                last_error = exc
                continue

        if payload is None:
            raise requests.RequestException(
                f"All JSON endpoints failed for r/{subreddit_name}: {last_error}"
            )

        children = payload.get("data", {}).get("children", [])
        for child in children:
            if child.get("kind") != "t3": # check that the item is a post (kind "t3") before processing, as Reddit's JSON can include other types like comments or ads
                continue
            posts.append(_parse_post(child, subreddit_name)) # parse the post data and append it to the list of posts to be returned

        # Keep requests polite when scanning multiple subreddits in sequence.
        time.sleep(0.5)

    # handling various exceptions that can occur during the HTTP request and JSON parsing process, logging errors for debugging and reliability purposes.
    except requests.RequestException as exc:
        logging.error("Error fetching r/%s via JSON API: %s", subreddit_name, exc)
    except ValueError as exc:
        logging.error("Invalid JSON for r/%s: %s", subreddit_name, exc)
    except Exception as exc:
        logging.error("Unexpected error for r/%s: %s", subreddit_name, exc)

    return posts
