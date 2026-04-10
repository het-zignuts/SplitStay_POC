from __future__ import annotations

import re
from typing import Iterable


def _normalize(text: str) -> str:
    """Lowercase text and collapse non-alphanumeric characters into spaces."""
    normalized = re.sub(r"[^a-z0-9]+", " ", (text or "").lower()) # replaces non-alphanumeric characters with spaces and converts to lowercase
    return re.sub(r"\s+", " ", normalized).strip() # collapses multiple spaces into a single space and trims leading/trailing whitespace


def _contains_phrase(text: str, phrase: str) -> bool:
    """Return whether a normalized phrase appears in normalized text."""
    normalized_phrase = _normalize(phrase)
    if not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {text} "


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    """Remove duplicates while preserving the first-seen order."""
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values


def is_relevant(
    post: dict,
    keywords: Iterable[str],
    keyword_groups: Iterable[Iterable[str]] | None = None,
) -> tuple[bool, list[str]]:
    """Return whether a post matches configured phrases or grouped keyword patterns."""
    text = _normalize(f"{post.get('title', '')} {post.get('body', '')}")

    matched_phrases = [
        phrase for phrase in keywords if phrase and _contains_phrase(text, phrase)
    ]

    matched_groups: list[str] = []
    for group in keyword_groups or []:
        normalized_group = [_normalize(part) for part in group if _normalize(part)]
        if normalized_group and all(_contains_phrase(text, part) for part in normalized_group):
            matched_groups.append(" + ".join(group))

    matched = _dedupe_preserve_order([*matched_phrases, *matched_groups])
    return len(matched) > 0, matched
