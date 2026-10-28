from __future__ import annotations

import re
from typing import Iterable


def _normalize(text: str) -> str:
    """Lowercase text and collapse non-alphanumeric characters into spaces."""
    normalized = re.sub(r"[^a-z0-9]+", " ", (text or "").lower()) # replaces non-alphanumeric characters with spaces and converts to lowercase
    return re.sub(r"\s+", " ", normalized).strip() # collapses multiple spaces into a single space and trims leading/trailing whitespace


def _contains_phrase(text: str, phrase: str) -> bool:
    """Return whether a normalized phrase appears in normalized text."""
    normalized_phrase = _normalize(phrase) # normalize the input phrase for consistent matching
    if not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {text} "


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    """Remove duplicates while preserving the first-seen order."""
    seen: set[str] = set() # set initialized to maintain seen values for deduplication
    unique_values: list[str] = [] # list initialized to store unique values while preserving order
    for value in values:
        if value in seen: # if the value has already been seen, skip it to avoid duplicates
            continue
        seen.add(value) # add the value to the seen set to track it for future duplicates
        unique_values.append(value) # append the unique value to the list to preserve order
    return unique_values


def is_relevant(
    post: dict,
    keywords: Iterable[str],
    keyword_groups: Iterable[Iterable[str]] | None = None,
) -> tuple[bool, list[str]]:
    """Return whether a post matches configured phrases or grouped keyword patterns."""
    text = _normalize(f"{post.get('title', '')} {post.get('body', '')}") # combine title and body of the post, normalize it for consistent matching

    # Check for explicit phrase matches first, then grouped keyword patterns.
    matched_phrases = [
        phrase for phrase in keywords if phrase and _contains_phrase(text, phrase)
    ]

    # Check for grouped keyword patterns.
    matched_groups: list[str] = []
    for group in keyword_groups or []:
        normalized_group = [_normalize(part) for part in group if _normalize(part)] # normalize keyword group values
        if normalized_group and all(_contains_phrase(text, part) for part in normalized_group): # check if all parts of the normalized group are present in the text
            matched_groups.append(" + ".join(group))

    matched = _dedupe_preserve_order([*matched_phrases, *matched_groups]) # combine matched phrases and groups, remove duplicates while preserving order
    return len(matched) > 0, matched # return whether any matches were found along with the list of matched keywords/groups
