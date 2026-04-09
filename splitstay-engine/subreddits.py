"""Subreddit groups and keyword constants used by the pipeline."""

SUBREDDITS = {
    "Music Festivals": ["coachella", "lollapalooza", "bonnaroo", "edm", "aves"],
    "Sports Events": ["nfl", "nba", "soccer", "formula1", "sports"],
    "Pop Culture": ["movies", "television", "hiphopheads", "kpop"],
    "General Travel": ["travel", "solotravel", "backpacking", "digitalnomad"],
}

KEYWORDS = {
    "Accommodation Sharing": ["share room", "shared room", "hotel share", "split stay", "split hotel"],
    "Roommate Seeking": ["roommate", "travel buddy", "looking for roommate", "need roommate"],
    "Cost Sharing": ["split cost", "split expenses", "share costs", "budget"],
    "Open Invitations": ["join me", "anyone joining", "open invite", "group trip"],
}

CATEGORY_BY_SUBREDDIT = {
    subreddit.lower(): category
    for category, sub_list in SUBREDDITS.items()
    for subreddit in sub_list
}
