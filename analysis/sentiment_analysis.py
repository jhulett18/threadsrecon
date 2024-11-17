# analysis/analyze.py

import pandas as pd
from textblob import TextBlob
from datetime import datetime
import json

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    try:
        analysis = TextBlob(str(text))
        return {
            'polarity': analysis.sentiment.polarity,
            'subjectivity': analysis.sentiment.subjectivity
        }
    except:
        return {'polarity': 0, 'subjectivity': 0}

def process_posts(posts_data):
    """Process posts into a pandas DataFrame with sentiment analysis"""
    processed_posts = []
    
    for post_key, post in posts_data.items():
        # Extract text and date
        text = post.get('text', '')
        date_posted = post.get('date_posted', '')
        
        # Perform sentiment analysis
        sentiment = analyze_sentiment(text)
        
        processed_posts.append({
            'post_id': post_key,
            'text': text,
            'date_posted': date_posted,
            'polarity': sentiment['polarity'],
            'subjectivity': sentiment['subjectivity']
        })
    
    return pd.DataFrame(processed_posts)
