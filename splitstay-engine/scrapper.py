from __future__ import annotations

from datetime import datetime
import logging
import time
from typing import Any

import requests

from config import settings

BASE_REDDIT_URL = "https://www.reddit.com"
FALLBACK_REDDIT_URL = "https://old.reddit.com"
POST_LIMIT = int(settings.POST_LIMIT)


def _normalize_url(permalink: str | None) -> str:
    if not permalink:
        return ""

    if permalink.startswith("http://") or permalink.startswith("https://"):
        return permalink

    return f"{BASE_REDDIT_URL}{permalink}"


def _parse_post(child: dict[str, Any], subreddit_name: str) -> dict[str, Any]:
    data = child.get("data", {})

    created_utc = data.get("created_utc")
    try:
        created = datetime.utcfromtimestamp(float(created_utc))
    except Exception:
        created = datetime.utcnow()

    return {
        "title": data.get("title") or "",
        "body": data.get("selftext") or "",
        "url": _normalize_url(data.get("permalink")) or data.get("url") or "",
        "author": data.get("author") or "",
        "subreddit": data.get("subreddit") or subreddit_name,
        "created": created,
    }


def get_posts(subreddit_name: str) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    endpoints = [
        f"{BASE_REDDIT_URL}/r/{subreddit_name}/new.json",
        f"{FALLBACK_REDDIT_URL}/r/{subreddit_name}/new.json",
    ]

    headers = {
        "User-Agent": settings.REDDIT_USER_AGENT,
        "Accept": "application/json",
    }

    params = {
        "limit": POST_LIMIT,
        "raw_json": 1,
    }

    try:
        payload: dict[str, Any] | None = None
        last_error: Exception | None = None

        for endpoint in endpoints:
            try:
                response = requests.get(
                    endpoint,
                    headers=headers,
                    params=params,
                    timeout=settings.REDDIT_REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                payload = response.json()
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
            if child.get("kind") != "t3":
                continue
            posts.append(_parse_post(child, subreddit_name))

        time.sleep(0.5)

    except requests.RequestException as exc:
        logging.error("Error fetching r/%s via JSON API: %s", subreddit_name, exc)
    except ValueError as exc:
        logging.error("Invalid JSON for r/%s: %s", subreddit_name, exc)
    except Exception as exc:
        logging.error("Unexpected error for r/%s: %s", subreddit_name, exc)

    return posts
