"""
Sentiment Analysis Module

This module provides functionality for analyzing sentiment in text data from social media posts.
It includes tools for sentiment scoring, hashtag extraction, and metadata parsing.

Note: NLTK imports are lazy-loaded to avoid delays during basic scraping operations.
"""

import pandas as pd
from textblob import TextBlob
from datetime import datetime
import json
import re
from collections import Counter

# Global variables for lazy-loaded NLTK components
_nltk_initialized = False
_sia = None
_stopwords_english = None

def _ensure_nltk_ready():
    """
    Lazy initialization of NLTK components.
    Only downloads and initializes NLTK when sentiment analysis is actually needed.
    """
    global _nltk_initialized, _sia, _stopwords_english
    
    if _nltk_initialized:
        return
    
    print("Initializing NLTK for sentiment analysis (one-time setup)...")
    
    # Import NLTK modules only when needed
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.sentiment import SentimentIntensityAnalyzer
    
    # Download necessary NLTK resources
    nltk.download('punkt', quiet=True)        # Tokenizer data
    nltk.download('punkt_tab', quiet=True)    # Additional tokenizer data
    nltk.download('stopwords', quiet=True)    # Common words to filter out
    nltk.download('vader_lexicon', quiet=True)  # Sentiment analysis lexicon
    
    # Initialize the VADER sentiment analyzer
    _sia = SentimentIntensityAnalyzer()
    _stopwords_english = set(stopwords.words('english'))
    _nltk_initialized = True
    
    print("NLTK sentiment analysis ready.")

def analyze_sentiment_nltk(text):
    """
    Analyze sentiment of text using NLTK's VADER SentimentIntensityAnalyzer
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: Dictionary containing sentiment scores:
            - neg: Negative sentiment score (0-1)
            - neu: Neutral sentiment score (0-1)
            - pos: Positive sentiment score (0-1)
            - compound: Normalized compound score (-1 to 1)
            
    Note:
        Returns zero scores if analysis fails
    """
    _ensure_nltk_ready()
    try:
        scores = _sia.polarity_scores(text)
        return scores
    except Exception as e:
        print(f"Error analyzing sentiment with NLTK: {str(e)}")
        return {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}

def extract_hashtags(text):
    """
    Extract hashtags from text using regex
    
    Args:
        text (str): Text to extract hashtags from
        
    Returns:
        list: List of hashtags found (without the # symbol)
        
    Example:
        >>> extract_hashtags("Hello #world #python")
        ['world', 'python']
    """
    hashtags = re.findall(r'#(\w+)', str(text))
    return hashtags

def parse_metadata(metadata_str):
    """
    Parse metadata string into engagement metrics
    
    Args:
        metadata_str (str): String containing engagement information
            Expected format: "X likes Y replies Z reposts"
            
    Returns:
        dict: Dictionary containing:
            - likes (int): Number of likes
            - replies (int): Number of replies
            - reposts (int): Number of reposts
            
    Example:
        >>> parse_metadata("5 likes 2 replies 1 repost")
        {'likes': 5, 'replies': 2, 'reposts': 1}
    """
    # Initialize default metrics
    metrics = {'likes': 0, 'replies': 0, 'reposts': 0}
    if not metadata_str:
        return metrics
    
    try:
        # Split metadata string into words
        parts = metadata_str.lower().split()
        i = 0
        while i < len(parts):
            current_part = parts[i]
            # Look ahead to check if next part exists and is a number
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                # Parse different types of engagement metrics
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
    """
    Process posts into a pandas DataFrame with sentiment analysis
    
    Args:
        posts_data (dict): Dictionary containing post data
            Expected format:
            {
                'post_id': {
                    'text': str,
                    'date_posted': str,
                    'metadata': str
                },
                ...
            }
            
    Returns:
        pandas.DataFrame: DataFrame containing processed posts with columns:
            - post_id: Unique identifier for the post
            - text: Original post text
            - date_posted: Timestamp of post
            - likes: Number of likes
            - replies: Number of replies
            - reposts: Number of reposts
            - neg: Negative sentiment score
            - neu: Neutral sentiment score
            - pos: Positive sentiment score
            - compound: Compound sentiment score
            - hashtags: List of hashtags used
            - hashtag_count: Number of hashtags used
            
    Note:
        - Handles missing data gracefully
        - Converts dates to datetime objects
        - Includes both sentiment analysis and engagement metrics
    """
    processed_posts = []
    
    for post_key, post in posts_data.items():
        try:
            # Extract and clean metadata
            metadata = post.get('metadata', '').replace(' Share', '')
            metrics = parse_metadata(metadata)

            text = post.get('text', '')

            # Perform sentiment analysis and hashtag extraction
            nltk_sentiment = analyze_sentiment_nltk(text)
            hashtags = extract_hashtags(text)

            # Create processed post entry
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
            })
        except Exception as e:
            print(f"Error processing post {post_key}: {str(e)}")
            continue
    
    # Convert to DataFrame and handle dates
    df = pd.DataFrame(processed_posts)
    if not df.empty:
        df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df
