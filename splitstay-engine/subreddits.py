# The variable SUBREDDITS defines the target subreddits to monitor, categorized by event type, 
# while KEYWORDS contains specific phrases to detect posts related to accommodation sharing. 
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

# The KEYWORDS dictionary contains specific phrases that are commonly associated with accommodation sharing, roommate seeking, cost sharing, and open invitations. 
# These phrases are used to identify relevant posts in the target subreddits.
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

# ALL_KEYWORDS is a flattened list of all individual keywords extracted from the grouped KEYWORDS dictionary, 
# which allows for straightforward matching against post content without needing to consider groupings.
ALL_KEYWORDS = [kw for group in KEYWORDS.values() for kw in group]

# KEYWORD_GROUPS is a list of keyword groups, where each group is a list of keywords.
# We use group matching to identify posts that may not contain explicit phrases but still indicate relevance through the presence of multiple related keywords.
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