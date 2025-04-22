import glob
import json
import os
import random
import time
from collections import defaultdict
from typing import Any, Dict

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("Please install Pydantic: pip install pydantic")
    exit(1)

from tqdm import tqdm

try:
    from openai import OpenAI
except ImportError:
    print("Please install the OpenAI package: pip install openai")
    exit(1)

# Initialize OpenAI client
# You'll need to set OPENAI_API_KEY as an environment variable
client = OpenAI()


# Define Pydantic models
class RedditAnalysisResult(BaseModel):
    reason: str = Field(
        ..., description="Explanation for verdict, including subject if applicable"
    )
    verdict: str = Field(..., description="Either Yes or No")


class ProcessedPost(BaseModel):
    post_id: str
    title: str
    subreddit: str
    selftext: str
    verdict: str
    reason: str


# Define prompt template
PROMPT_TEMPLATE = """
Analyze the following Reddit post and determine if the user is struggling with a
specific subject or topic and experiences loss of motivation, or the user is just
generally feeling hopeless.

Specifically, answer Yes if:
- The user discusses expireincing difficulty explicitly, e.g., "too hard".
- A specific subject is causing this difficulty, e.g., "trigonometry" or "funding"
- AND the user experices loss of motivation (e.g., "hopless", negative beliefs)

Othwerwise, answer No if:
- the user only mentions loss of motivation (e.g., "hopless", negative beliefs)
- AND NOT explicitly discussing the difficulty or a specific subject or topic

Title: {title}
Subreddit: {subreddit}
Content: {content}

Your analysis should be provided as a JSON object with two fields:
1. "verdict": Either "Yes" if the user is struggling with a specific 
   subject/topic, or "No" if it's a general loss of motivation or hopelessness.
2. "reason": A brief explanation of why you reached this conclusion, including 
   the specific subject/topic if applicable.
"""


def analyze_post(file_path):
    """Analyze a single Reddit post using GPT-4.1-mini"""
    # Read the post data
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            post_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {file_path}: {e}")
            return None

    # Extract relevant information
    title = post_data.get("title", "")
    subreddit = post_data.get("subreddit", "")
    content = post_data.get("selftext", "")
    post_id = post_data.get("id", "unknown")

    # Skip if no content to analyze
    if not content and not title:
        print(f"Skipping {post_id} - No content to analyze")
        return None

    # Prepare prompt
    prompt = PROMPT_TEMPLATE.format(title=title, subreddit=subreddit, content=content)

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # Using GPT-4.1-mini as specified
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in analyzing Reddit posts. Provide your "
                    "analysis in JSON format with 'verdict' and 'reason' fields as "
                    "specified in the prompt.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        analysis = response.choices[0].message.content

        # Parse the JSON response using Pydantic
        try:
            analysis_data = RedditAnalysisResult.model_validate_json(analysis)
            verdict = analysis_data.verdict
            reason = analysis_data.reason
        except Exception as e:
            print(f"Error parsing response for post {post_id}: {e}")
            verdict = "error"
            reason = f"Failed to parse response: {str(e)}"

        # Return results as a Pydantic model
        return ProcessedPost(
            post_id=post_id,
            title=title,
            subreddit=subreddit,
            selftext=content,
            verdict=verdict,
            reason=reason,
        )

    except Exception as e:
        print(f"Error analyzing post {post_id}: {e}")
        time.sleep(1)  # Rate limiting precaution
        return None


def main():
    # Define output file
    output_dir = "results"
    output_file = os.path.join(output_dir, "reddit_analysis_results.json")

    # Create the results directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all JSON files in the reddit_data directory and its subdirectories
    data_paths = glob.glob("reddit_data/**/*.json", recursive=True)
    print(f"Found {len(data_paths)} posts to analyze")

    # Subsample 10 random paths if we have more than 10 posts
    if len(data_paths) > 10:
        data_paths = random.sample(data_paths, 10)
        print("Subsampled to 10 random posts for analysis")

    results = []

    # Process each post
    positive_verdicts = 0
    subreddit_to_positive_ids = defaultdict(list)
    for file_path in tqdm(data_paths, desc="Analyzing posts"):
        result = analyze_post(file_path)

        if result:
            results.append(result.model_dump())
            if result.verdict == "Yes":
                positive_verdicts += 1
                subreddit = file_path.split("/")[1]
                subreddit_to_positive_ids[subreddit].append(result.post_id)

            # Save intermediate results periodically
            if len(results) % 10 == 0 or len(results) == len(data_paths):
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
                print(f"Saved {len(results)} results to {output_file}")

        # Add a small delay to avoid rate limiting
        time.sleep(0.5)

    # dump subreddit_to_positive_ids to a json file
    with open(
        os.path.join(output_dir, "subreddit_to_positive_ids.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(subreddit_to_positive_ids, f, indent=2)

    print(f"Analysis complete. Total posts analyzed: {len(results)}")
    print(f"Positive verdicts: {positive_verdicts}")


if __name__ == "__main__":
    main()
