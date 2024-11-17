import json
from datetime import datetime
import pandas as pd
from analysis.sentiment_analysis import process_posts 

class DataProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = self.load_data()
        
    def load_data(self):
        """Load JSON data from file"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def filter_by_date(self, df, start_date=None, end_date=None):
        """Filter DataFrame by date range"""
        if start_date:
            df = df[df['date_posted'] >= start_date]
        if end_date:
            df = df[df['date_posted'] <= end_date]
        return df
    
    def filter_by_keywords(self, df, keywords):
        """Filter DataFrame by keywords in text"""
        if not keywords:
            return df
        
        pattern = '|'.join(keywords)
        return df[df['text'].str.contains(pattern, case=False, na=False)]
    
    def process_and_archive(self, output_file, keywords=None, start_date=None, end_date=None):
        """Process, filter and archive data"""
        all_posts_data = []
        
        # Process each profile
        for username, profile_data in self.data.items():
            if isinstance(profile_data, dict) and 'posts' in profile_data.get(username, {}):
                posts = profile_data[username]['posts']
                posts_df = process_posts(posts)
                posts_df['username'] = username
                all_posts_data.append(posts_df)
        
        # Combine all posts
        if all_posts_data:
            combined_df = pd.concat(all_posts_data, ignore_index=True)
            
            # Apply filters
            filtered_df = self.filter_by_date(combined_df, start_date, end_date)
            filtered_df = self.filter_by_keywords(filtered_df, keywords)
            
            # Save to file
            result = {
                'metadata': {
                    'total_posts': len(filtered_df),
                    'processed_date': datetime.now().isoformat(),
                    'filters_applied': {
                        'keywords': keywords,
                        'date_range': {
                            'start': start_date,
                            'end': end_date
                        }
                    }
                },
                'posts': filtered_df.to_dict('records')
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            
            return result
        
        return None