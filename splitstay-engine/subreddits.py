"""Subreddit groups and keyword constants used by the pipeline."""

SUBREDDITS = {
    "Music Festivals": ["festivals", "Coachella", "glastonbury", "bonnaroo", "electricdaisycarnival"],
    "Sports Events": ["formula1", "soccer", "nfl", "SuperBowl", "olympics"],
    "Pop Culture": ["concerts", "TaylorSwift", "comiccon", "beyonce"],
    "General Travel": ["travel", "solotravel", "couchsurfing", "digitalnomad"],
}

KEYWORDS = {
    "Accommodation Sharing": ["split hotel", "share hotel", "share airbnb", "share room", "split room", "share accommodation", "share booking"],
    "Roommate Seeking": ["looking for roommate", "need a roommate", "hotel buddy", "room buddy", "anyone to split"],
    "Cost Sharing": ["split cost", "half the cost", "share cost", "split the bill", "going halves"],
    "Open Invitations": ["anyone want to share", "does anyone want to split", "looking to share", "open to sharing"],
}

CATEGORY_BY_SUBREDDIT = {
    subreddit.lower(): category
    for category, sub_list in SUBREDDITS.items()
    for subreddit in sub_list
}
