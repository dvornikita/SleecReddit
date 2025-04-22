# SleecReddit Scraper and Analyzer

A Python program that scrapes posts from specified subreddits, saves them to your local drive, and provides powerful analysis capabilities using OpenAI's GPT models.

## Features

- Scrapes posts from r/HomeworkHelp, r/AskAcademia, r/AcademicHelp, and r/Student
- Focuses on posts from the last year
- Saves each post as an individual JSON file
- Excludes comments, focusing only on the main posts
- Analyzes post content using OpenAI's GPT models to:
  - Extract key topics and themes
  - Identify common patterns in questions
  - Generate insights about student needs
  - Summarize trends across subreddits

## Setup

1. Make sure you have Python 3.6+ installed
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a Reddit API application:
   - Go to https://www.reddit.com/prefs/apps
   - Click the "create app" or "create another app" button
   - Fill in the name, select "script", and put "http://localhost:8080" in the redirect URI
   - After creating the app, note the client ID (under the app name) and client secret

4. Get an OpenAI API key:
   - Go to https://platform.openai.com/
   - Sign up or log in to your account
   - Navigate to the API keys section
   - Create a new API key

5. Create a `.env` file based on the `.env.example` file:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file and add your Reddit API credentials and OpenAI API key.

## Usage

### Scraping Data

Run the scraping script with:

```
python reddit_scraper.py
```

The script will:
1. Connect to the Reddit API
2. Fetch posts from the specified subreddits from the last year
3. Save each post as an individual JSON file in the `data/` directory, organized by subreddit

### Analyzing Data

Run the analysis script with:

```
python reddit_analyzer.py [options]
```

Available options:
- `--subreddit`: Analyze a specific subreddit (default: all)
- `--timeframe`: Analyze posts from a specific timeframe (e.g., "1m", "6m", "1y")
- `--output`: Specify output format (json, csv, txt)
- `--analysis-type`: Choose analysis type:
  - `topics`: Extract main topics and themes
  - `patterns`: Identify common question patterns
  - `trends`: Generate trend analysis
  - `summary`: Create a comprehensive summary
  - `all`: Perform all analyses (default)

Example:
```
python reddit_analyzer.py --subreddit HomeworkHelp --timeframe 3m --analysis-type patterns
```

## Output

### Scraping Output

The script creates a directory structure like:

```
data/
├── HomeworkHelp/
│   ├── Post_Title_1_postid.json
│   ├── Post_Title_2_postid.json
│   └── ...
├── AskAcademia/
│   ├── Post_Title_1_postid.json
│   ├── Post_Title_2_postid.json
│   └── ...
├── AcademicHelp/
│   ├── Post_Title_1_postid.json
│   ├── Post_Title_2_postid.json
│   └── ...
└── Student/
    ├── Post_Title_1_postid.json
    ├── Post_Title_2_postid.json
    └── ...
```

Each JSON file contains a post object with fields like:
- `id`: The Reddit post ID
- `title`: The post title
- `author`: The Reddit username of the poster
- `created_date`: When the post was created
- `selftext`: The content of the post
- And other metadata

### Analysis Output

Analysis results are saved in the `analysis/` directory with the following structure:

```
analysis/
├── topics/
│   ├── HomeworkHelp_topics_2024_03.json
│   └── ...
├── patterns/
│   ├── AskAcademia_patterns_2024_Q1.json
│   └── ...
├── trends/
│   ├── monthly_trends.json
│   └── yearly_trends.json
└── summaries/
    ├── daily_summaries/
    └── weekly_summaries/
```

Each analysis file contains structured data about the findings, including:
- Identified topics and their frequencies
- Common question patterns and examples
- Trend analysis with statistical data
- Generated summaries and insights

## Note

This script respects Reddit's API rate limits and follows ethical scraping practices. However, be aware that:
- Reddit's API terms may change, and excessive requests might be rate-limited
- OpenAI API usage incurs costs based on your usage
- Large-scale analysis may take significant time and API credits 