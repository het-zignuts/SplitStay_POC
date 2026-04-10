# """Subreddit groups and keyword constants used by the pipeline."""

# # These groups drive subreddit scanning and provide the default category label.
# SUBREDDITS = {
#     "Music Festivals": ["festivals", "Coachella", "glastonbury", "bonnaroo", "electricdaisycarnival"],
#     "Sports Events": ["formula1", "soccer", "nfl", "SuperBowl", "olympics"],
#     "Pop Culture": ["concerts", "TaylorSwift", "comiccon", "beyonce"],
#     "General Travel": ["travel", "solotravel", "couchsurfing", "digitalnomad"],
#     # "Accommodation Sharing": ["airbnb", "hotels", "hostelworld", "travelpartners"],
# }

# KEYWORDS = {
#     "Accommodation Sharing": [
#         "share",
#         "split",
#         "room",
#         "hotel",
#         "airbnb",
#         "accommodation",
#         "booking",
#         "condo",
#         "apartment",
#         "hostel",
#     ],
#     "Roommate Seeking": [
#         "roommate",
#         "roomie",
#         "buddy",
#         "partner",
#         "travel",
#         "share",
#         "split",
#         "looking",
#         "need",
#         "anyone",
#     ],
#     "Cost Sharing": [
#         "cost",
#         "costs",
#         "expense",
#         "expenses",
#         "bill",
#         "half",
#         "halves",
#         "share",
#         "split",
#         "price",
#     ],
#     "Open Invitations": [
#         "anyone",
#         "open",
#         "join",
#         "invite",
#         "interested",
#         "share",
#         "split",
#         "together",
#         "with",
#         "company",
#     ],
# }

# # Precompute lowercase subreddit-to-category lookups for the ingestion loop.
# CATEGORY_BY_SUBREDDIT = {
#     subreddit.lower(): category
#     for category, sub_list in SUBREDDITS.items()
#     for subreddit in sub_list
# }

SUBREDDITS = {
    "Music Festivals": [
        "festivals", "Coachella", "glastonbury", "bonnaroo", "electricdaisycarnival"
    ],
    "Sports Events": [
        "formula1", "soccer", "nfl", "SuperBowl", "olympics"
    ],
    "Pop Culture": [
        "concerts", "TaylorSwift", "comiccon", "beyonce"
    ],
    "General Travel": [
        "solotravel", "travel", "digitalnomad", "couchsurfing"
    ]
}

KEYWORDS = {
    "Accommodation Sharing": [
        "split hotel", "share hotel", "share airbnb", "split airbnb",
        "share room", "split room", "share accommodation", "share booking",
        "share an airbnb", "share my airbnb", "sharing a hotel",
        "share a condo", "split accommodation"
    ],
    "Roommate Seeking": [
        "looking for roommate", "need a roommate", "hotel buddy",
        "room buddy", "travel buddy", "anyone to split",
        "looking for a roommate", "looking for someone to share",
        "looking for a travel partner"
    ],
    "Cost Sharing": [
        "split cost", "half the cost", "share cost",
        "split the bill", "going halves", "split costs",
        "share costs", "split expenses"
    ],
    "Open Invitations": [
        "anyone want to share", "does anyone want to split",
        "looking to share", "open to sharing",
        "anyone want to share a room"
    ]
}

ALL_KEYWORDS = [kw for group in KEYWORDS.values() for kw in group]

KEYWORD_GROUPS = [
    ["share", "airbnb"],
    ["split", "airbnb"],
    ["share", "hotel"],
    ["split", "hotel"],
    ["share", "room"],
    ["split", "room"],
    ["share", "accommodation"],
    ["split", "accommodation"],
    ["share", "cost"],
    ["split", "cost"],
    ["share", "expense"],
    ["split", "expense"],
    ["travel", "buddy"],
    ["hotel", "buddy"],
    ["room", "buddy"],
    ["roommate", "travel"],
    ["looking for", "roommate"],
    ["looking for", "share"],
]