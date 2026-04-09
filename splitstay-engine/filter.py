def is_relevant(post, keywords):
    text = (post["title"] + " " + post["body"]).lower()
    matched = [k for k in keywords if k in text]
    return len(matched) > 0, matched