# analysis/analyze.py

import json
from textblob import TextBlob
from datetime import datetime

def extract_hashtags(text):
    return [word for word in text.split() if word.startswith("#")]

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return sentiment.polarity, sentiment.subjectivity

def filter_data(posts, keyword_filter, date_filter):
    filtered = []
    for post in posts:
        if keyword_filter in post["hashtags"] and post["date_posted"] >= date_filter:
            filtered.append(post)
    return filtered

def process_entry(entry_type, entries):
    processed_entries = []
    for key, entry in entries.items():
        text = entry["text"]
        date_posted = entry["date_posted"]
        hashtags = extract_hashtags(text)
        polarity, subjectivity = analyze_sentiment(text)
        processed_entries.append({
            "id": key,
            "text": text,
            "date_posted": date_posted,
            "hashtags": hashtags,
            "polarity": polarity,
            "subjectivity": subjectivity
        })
    return processed_entries

def analyze_and_filter_data(input_file, output_file, filtered_file, keyword_filter, date_filter):
    # Load the data from the profiles JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Print the data to inspect its structure (optional)
    print("Data loaded from file:", data)

    # Create a list to store filtered posts
    filtered_posts = []

    # Iterate over each profile in the data
    for username, profile_data in data.items():
        # Ensure that the profile has 'posts' key
        if "posts" in profile_data:
            posts = profile_data["posts"]

            # Filter posts by keyword and date
            for post_id, post in posts.items():
                post_text = post.get('text', '')
                post_date = post.get('date_posted', '')

                # Apply keyword filter
                if keyword_filter.lower() in post_text.lower():
                    # Apply date filter (assuming it's a valid ISO 8601 datetime string)
                    if post_date >= date_filter:
                        filtered_posts.append({
                            "username": username,
                            "post_id": post_id,
                            "text": post_text,
                            "date_posted": post_date
                        })

    # Save the filtered posts to a JSON file
    with open(filtered_file, 'w') as f:
        json.dump(filtered_posts, f, indent=4)

    # Optionally, save all data to an archived JSON file (if needed)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Filtered data saved to {filtered_file}")