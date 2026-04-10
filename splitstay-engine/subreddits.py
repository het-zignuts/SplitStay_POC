"""Subreddit groups and keyword constants used by the pipeline."""

SUBREDDITS = {
    "Music Festivals": ["festivals", "Coachella", "glastonbury", "bonnaroo", "electricdaisycarnival"],
    "Sports Events": ["formula1", "soccer", "nfl", "SuperBowl", "olympics"],
    "Pop Culture": ["concerts", "TaylorSwift", "comiccon", "beyonce"],
    "General Travel": ["travel", "solotravel", "couchsurfing", "digitalnomad"],
    # "Accommodation Sharing": ["airbnb", "hotels", "hostelworld", "travelpartners"],
}

KEYWORDS = {
    "Accommodation Sharing": [
        "share",
        "split",
        "room",
        "hotel",
        "airbnb",
        "accommodation",
        "booking",
        "condo",
        "apartment",
        "hostel",
    ],
    "Roommate Seeking": [
        "roommate",
        "roomie",
        "buddy",
        "partner",
        "travel",
        "share",
        "split",
        "looking",
        "need",
        "anyone",
    ],
    "Cost Sharing": [
        "cost",
        "costs",
        "expense",
        "expenses",
        "bill",
        "half",
        "halves",
        "share",
        "split",
        "price",
    ],
    "Open Invitations": [
        "anyone",
        "open",
        "join",
        "invite",
        "interested",
        "share",
        "split",
        "together",
        "with",
        "company",
    ],
}

CATEGORY_BY_SUBREDDIT = {
    subreddit.lower(): category
    for category, sub_list in SUBREDDITS.items()
    for subreddit in sub_list
}
