import datetime
import json
import os
from pathlib import Path

import praw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "SleecReddit scraper by /u/YourUsername")

# Subreddits to scrape
SUBREDDITS = ["HomeworkHelp", "AskAcademia", "Student"]

# Output directory
OUTPUT_DIR = Path("reddit_data")


def setup():
    """Set up the Reddit API client and output directory."""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Reddit API credentials not found.")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in your .env file.")
        print(
            "You can get these by creating a Reddit app at https://www.reddit.com/prefs/apps"
        )
        exit(1)

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Initialize Reddit client
    reddit = praw.Reddit(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT
    )

    return reddit


def get_posts_from_last_n_years(reddit, subreddit_name, n_years):
    """Get posts from the last n years for a given subreddit."""
    subreddit = reddit.subreddit(subreddit_name)

    # Calculate timestamp for n years ago
    n_years_ago = int(
        (datetime.datetime.now() - datetime.timedelta(days=n_years * 365)).timestamp()
    )

    posts = []

    print(f"Collecting posts from r/{subreddit_name} from the last {n_years} years...")

    # First get posts from the 'new' section
    for post in subreddit.new(limit=None):
        if post.created_utc > n_years_ago and not post.url.endswith(
            (".jpg", ".jpeg", ".png", ".gif")
        ):
            posts.append(extract_post_data(post))
        else:
            break

    # Also get posts from 'top' of the year to ensure we don't miss popular ones
    for post in subreddit.top("all", limit=None):
        post_data = extract_post_data(post)
        # Check if this post is already in our list and doesn't have an image
        if not any(p["id"] == post_data["id"] for p in posts) and not post.url.endswith(
            (".jpg", ".jpeg", ".png", ".gif")
        ):
            posts.append(post_data)

    print(f"Collected {len(posts)} posts from r/{subreddit_name}")
    return posts


def extract_post_data(post):
    """Extract relevant data from a post."""
    return {
        "id": post.id,
        "subreddit": post.subreddit.display_name,
        "title": post.title,
        "author": str(post.author) if post.author else "[deleted]",
        "created_utc": post.created_utc,
        "created_date": datetime.datetime.fromtimestamp(post.created_utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "score": post.score,
        "upvote_ratio": post.upvote_ratio,
        "url": post.url,
        "permalink": f"https://www.reddit.com{post.permalink}",
        "selftext": post.selftext,
    }


def save_post(post, subreddit_name):
    """Save a single post to its own file."""
    # Create subreddit directory if it doesn't exist
    subreddit_dir = OUTPUT_DIR / subreddit_name
    subreddit_dir.mkdir(exist_ok=True)

    # Create a safe filename from the post title
    # Remove any characters that might cause issues in filenames
    safe_title = "".join(c for c in post["title"] if c.isalnum() or c in " -_").strip()
    safe_title = safe_title[:50]  # Truncate if too long
    if not safe_title:  # If title is empty or has no valid characters
        safe_title = "untitled"

    # Append post ID to ensure uniqueness
    file_name = f"{safe_title}_{post['id']}.json"
    file_path = subreddit_dir / file_name

    # Save the post data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=2)

    return file_path


def save_posts(posts, subreddit_name):
    """Save all posts to individual files."""
    print(f"Saving {len(posts)} posts from r/{subreddit_name}...")

    file_paths = []
    for post in posts:
        file_path = save_post(post, subreddit_name)
        file_paths.append(file_path)

    print(f"Saved {len(file_paths)} posts to {OUTPUT_DIR}/{subreddit_name}/")
    return file_paths


def main():
    """Main function to scrape Reddit posts."""
    reddit = setup()

    all_saved_paths = []
    n_years = 3  # You can change this value to the desired number of years
    for subreddit_name in SUBREDDITS:
        posts = get_posts_from_last_n_years(reddit, subreddit_name, n_years)
        saved_paths = save_posts(posts, subreddit_name)
        all_saved_paths.extend(saved_paths)

    print(
        f"Done! All {len(all_saved_paths)} posts have been saved to the {OUTPUT_DIR} directory."
    )


if __name__ == "__main__":
    main()
