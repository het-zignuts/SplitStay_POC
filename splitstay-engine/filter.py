from __future__ import annotations

import re


def _normalize(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
    return re.sub(r"\s+", " ", normalized).strip()


def is_relevant(post, keywords):
    text = _normalize(f"{post.get('title', '')} {post.get('body', '')}")
    token_set = set(text.split())
    matched = [word for word in keywords if word and word.lower() in token_set]
    return len(matched) > 0, matched
