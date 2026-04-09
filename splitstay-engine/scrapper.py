import os
import praw
from datetime import datetime
from config import settings
import time

reddit = praw.Reddit(
    client_id=settings.REDDIT_CLIENT_ID,
    client_secret=settings.REDDIT_CLIENT_SECRET,
    user_agent=settings.REDDIT_USER_AGENT
)

POST_LIMIT = int(settings.POST_LIMIT)

def get_posts(subreddit_name):
    posts = []

    try:
        subreddit = reddit.subreddit(subreddit_name)

        for post in subreddit.new(limit=POST_LIMIT):
            posts.append({
                "title": post.title or "",
                "body": post.selftext or "",
                "url": post.url,
                "author": str(post.author),
                "subreddit": subreddit_name,
                "created": datetime.utcfromtimestamp(post.created_utc)
            })

        time.sleep(0.5)  

    except Exception as e:
        print(f"Error fetching r/{subreddit_name}: {e}")

    return posts