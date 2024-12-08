# analysis/analyze.py

import pandas as pd
from textblob import TextBlob
from datetime import datetime
import json
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('vader_lexicon')

# Initialize SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment_nltk(text):
    """Analyze sentiment of text using NLTK SentimentIntensityAnalyzer"""
    try:
        scores = sia.polarity_scores(text)
        return scores
    except Exception as e:
        print(f"Error analyzing sentiment with NLTK: {str(e)}")
        return {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}

def tokenize_and_filter(text):
    """Tokenize text and remove stopwords"""
    try:
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word.isalnum() and word.lower() not in stop_words]
        return filtered_tokens
    except Exception as e:
        print(f"Error tokenizing text: {str(e)}")
        return []

def extract_keywords(text):
    """Extract keywords based on frequency"""
    tokens = tokenize_and_filter(text)
    keyword_counts = Counter(tokens)
    return keyword_counts.most_common(5)  # Return top 5 keywords

def extract_hashtags(text):
    """Extract hashtags from text"""
    hashtags = re.findall(r'#(\w+)', str(text))
    return hashtags

def parse_metadata(metadata_str):
    """Parse metadata string into metrics"""
    metrics = {'likes': 0, 'replies': 0, 'reposts': 0}
    if not metadata_str:
        return metrics
    
    try:
        parts = metadata_str.lower().split()
        i = 0
        while i < len(parts):
            current_part = parts[i]
            # Look ahead to check if next part exists and is a number
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                # Convert number words to digits if needed
                if current_part == 'like' or current_part == 'likes':
                    try:
                        metrics['likes'] = int(next_part)
                    except ValueError:
                        pass
                elif current_part == 'reply' or current_part == 'replies':
                    try:
                        metrics['replies'] = int(next_part)
                    except ValueError:
                        pass
                elif current_part == 'repost' or current_part == 'reposts':
                    try:
                        metrics['reposts'] = int(next_part)
                    except ValueError:
                        pass
            i += 1
    except Exception as e:
        print(f"Error parsing metadata: {str(e)}")
    return metrics

def process_posts(posts_data):
    """Process posts into a pandas DataFrame with sentiment analysis"""
    processed_posts = []
    
    for post_key, post in posts_data.items():
        try:
            # Extract metadata metrics
            metadata = post.get('metadata', '').replace(' Share', '')
            metrics = parse_metadata(metadata)

            # Tokenize and extract keywords
            text = post.get('text', '')
            tokens = tokenize_and_filter(text)
            keywords = extract_keywords(text)

            # Get sentiment
            nltk_sentiment = analyze_sentiment_nltk(text)
            hashtags = extract_hashtags(text)

            processed_posts.append({
                'post_id': post_key,
                'text': text,
                'date_posted': post.get('date_posted', ''),
                'likes': metrics.get('likes', 0),
                'replies': metrics.get('replies', 0),
                'reposts': metrics.get('reposts', 0),
                'neg': nltk_sentiment['neg'],
                'neu': nltk_sentiment['neu'],
                'pos': nltk_sentiment['pos'],
                'compound': nltk_sentiment['compound'],
                'hashtags': hashtags,
                'hashtag_count': len(hashtags),
                'tokens': tokens,
                'keywords': keywords
            })
        except Exception as e:
            print(f"Error processing post {post_key}: {str(e)}")
            continue
    
    df = pd.DataFrame(processed_posts)
    if not df.empty:
        df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df
