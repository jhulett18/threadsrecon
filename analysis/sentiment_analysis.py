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
        try:
            # Extract metadata metrics
            metadata = post.get('metadata', ''). replace(' Share','')
            metrics = {}
            if metadata:
                parts = metadata.split()
                for i in range(0, len(parts)-1, 2):  # Step by 2 to process pairs
                    if i+1 < len(parts):  # Check if we have both parts
                        metric = parts[i].lower()
                        try:
                            value = int(parts[i+1])
                            if metric == 'like':
                                metrics['likes'] = value
                            elif metric == 'reply':
                                metrics['replies'] = value
                            elif metric == 'repost':
                                metrics['reposts'] = value
                        except ValueError:
                            continue

            # Get sentiment
            sentiment = analyze_sentiment(post.get('text', ''))
            
            processed_posts.append({
                'post_id': post_key,
                'text': post.get('text', ''),
                'date_posted': post.get('date_posted', ''),
                'likes': metrics.get('likes', 0),
                'replies': metrics.get('replies', 0),
                'reposts': metrics.get('reposts', 0),
                'polarity': sentiment['polarity'],
                'subjectivity': sentiment['subjectivity']
            })
            
        except Exception as e:
            print(f"Error processing post {post_key}: {str(e)}")
            continue
    
    df = pd.DataFrame(processed_posts)
    if not df.empty:
        df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df

def parse_metadata(metadata_str):
    """Parse metadata string into metrics"""
    metrics = {'likes': 0, 'replies': 0, 'reposts': 0}
    if not metadata_str:
        return metrics
        
    try:
        parts = metadata_str.split()
        for i, part in enumerate(parts):
            if part.lower() == 'like':
                metrics['likes'] = int(parts[i+1])
            elif part.lower() == 'reply':
                metrics['replies'] = int(parts[i+1])
            elif part.lower() == 'repost':
                metrics['reposts'] = int(parts[i+1])
    except:
        pass
    
    return metrics