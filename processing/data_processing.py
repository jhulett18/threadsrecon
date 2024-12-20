"""
Data Processing Module

This module handles the processing, analysis, and archiving of social media data.
It includes functionality for:
- Loading and processing JSON data
- Analyzing mutual follower relationships
- Processing hashtags and engagement metrics
- Integrating with warning systems
- Archiving processed data
"""

import json
from datetime import datetime
import pandas as pd
import asyncio
from analysis.sentiment_analysis import process_posts
from visualization.visualization import HashtagNetworkAnalyzer 
from warningsys.warning_system import TelegramAlertSystem, KeywordMonitor
from functools import lru_cache


class DataProcessor:
    """
    A class to process and analyze social media data
    
    This class handles:
    - Data loading and validation
    - Mutual follower analysis
    - Hashtag statistics
    - Integration with warning systems
    - Data archiving
    
    Attributes:
        input_file (str): Path to input JSON data file
        data (dict): Loaded and processed data
        keyword_monitor (KeywordMonitor): Optional warning system integration
    """

    def __init__(self, input_file, telegram_token=None, chat_id=None, priority_keywords=None):
        """
        Initialize the DataProcessor
        
        Args:
            input_file (str): Path to JSON data file
            telegram_token (str, optional): Telegram bot API token for alerts
            chat_id (str, optional): Telegram chat ID for alerts
            priority_keywords (dict, optional): Keywords to monitor by priority level
        """
        self.input_file = input_file
        self.data = self.load_data()
        self.add_mutual_follower_status()
        
        # Initialize the warning system if credentials are provided
        self.keyword_monitor = None
        if telegram_token and chat_id:
            self.keyword_monitor = KeywordMonitor(telegram_token, chat_id, priority_keywords)

    def load_data(self):
        """
        Load JSON data from file
        
        Returns:
            dict: Loaded data or empty dict if file not found
            
        Note:
            Creates empty data structure if file doesn't exist
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Input file {self.input_file} not found. Creating empty data structure.")
            return {}

    def add_mutual_follower_status(self):
        """
        Add mutual follower status to all user relationships
        
        Processes the data to:
        1. Identify mutual following relationships
        2. Add 'is_mutual' field to follower/following entries
        3. Handle nested data structures
        
        Note:
            Updates the data in-place
        """
        for username, outer_profile in self.data.items():
            # Handle the double nesting of profile data
            profile_data = outer_profile.get(username, {})
            
            if isinstance(profile_data, dict):
                followers = profile_data.get('followers', {})
                following = profile_data.get('following', {})
                
                # Extract usernames from nested structures
                follower_usernames = {v['username'] for k, v in followers.items() 
                                   if isinstance(v, dict) and 'username' in v}
                following_usernames = {v['username'] for k, v in following.items() 
                                    if isinstance(v, dict) and 'username' in v}
                
                # Update followers with mutual status
                for _, follower_data in followers.items():
                    if isinstance(follower_data, dict) and 'username' in follower_data:
                        is_mutual = follower_data['username'] in following_usernames
                        follower_data['is_mutual'] = is_mutual
                
                # Update following with mutual status
                for _, following_data in following.items():
                    if isinstance(following_data, dict) and 'username' in following_data:
                        is_mutual = following_data['username'] in follower_usernames
                        following_data['is_mutual'] = is_mutual

                # Update the profile data
                profile_data['followers'] = followers
                profile_data['following'] = following
                outer_profile[username] = profile_data

    @lru_cache(maxsize=32)
    def get_hashtag_stats(self, username=None):
        """
        Get hashtag usage statistics for specified user or all users
        
        Args:
            username (str, optional): Specific username to analyze. If None, analyzes all users.
            
        Returns:
            dict: Statistics including:
                - total_hashtags: Total number of hashtags used
                - unique_hashtags: Number of unique hashtags
                - top_hashtags: Most frequently used hashtags
                - avg_hashtags_per_post: Average hashtags per post
                
        Note:
            Results are cached using lru_cache for performance
        """
        all_posts_data = []
        
        if username:
            # Process single user's posts
            outer_profile = self.data.get(username, {})
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
        else:
            # Process all users' posts
            for username, outer_profile in self.data.items():
                if isinstance(outer_profile, dict):
                    inner_profile = outer_profile.get(username, {})
                    posts = inner_profile.get('posts', {})
                    if posts:
                        posts_df = process_posts(posts)
                        posts_df['username'] = username
                        all_posts_data.append(posts_df)
        
        combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
        
        if combined_df.empty:
            return {
                'total_hashtags': 0,
                'unique_hashtags': 0,
                'top_hashtags': [],
                'avg_hashtags_per_post': 0
            }
        
        # Analyze hashtag usage
        hashtag_series = combined_df.explode('hashtags')['hashtags']
        hashtag_counts = hashtag_series.value_counts()
        
        return {
            'total_hashtags': len(hashtag_series.dropna()),
            'unique_hashtags': len(hashtag_counts),
            'top_hashtags': hashtag_counts.head(10).to_dict(),
            'avg_hashtags_per_post': combined_df['hashtag_count'].mean()
        }
        
    def analyze_hashtag_network(self):
        """Analyze and visualize hashtag network"""
        # Collect all posts
        all_posts_data = []
        for username, outer_profile in self.data.items():
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
        
        combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
        
        if combined_df.empty:
            return None
            
        analyzer = HashtagNetworkAnalyzer(combined_df)
        
        # Create both visualizations
        static_fig = analyzer.plot_matplotlib()
        interactive_fig = analyzer.plot_plotly()
        
        return {
            'static': static_fig,
            'interactive': interactive_fig,
            'total_connections': len(analyzer.edge_weights),
            'strongest_connections': sorted(
                [(tags, weight) for tags, weight in analyzer.edge_weights.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    def analyze_sentiment_trends(self):
        """Analyze and visualize sentiment trends across all posts"""
        # Collect all posts
        all_posts_data = []
        for username, outer_profile in self.data.items():
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
        
        combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
        
        if combined_df.empty:
            return None
            
        analyzer = HashtagNetworkAnalyzer(combined_df)
        return analyzer.plot_sentiment_trends(combined_df)

    def analyze_engagement_metrics(self):
        """Analyze and visualize engagement metrics across all posts"""
        # Collect all posts
        all_posts_data = []
        for username, outer_profile in self.data.items():
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
        
        combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
        
        if combined_df.empty:
            return None
            
        analyzer = HashtagNetworkAnalyzer(combined_df)
        return analyzer.plot_engagement_metrics(combined_df)

    def analyze_mutual_followers(self):
        """Analyze and visualize mutual followers network"""
        analyzer = HashtagNetworkAnalyzer(pd.DataFrame())  # Empty DataFrame since we don't need it for this visualization
        return analyzer.plot_mutual_followers_network(self.data)

    def analyze_hashtag_distribution(self):
        """Analyze and visualize hashtag distribution"""
        # Collect all posts
        all_posts_data = []
        for username, outer_profile in self.data.items():
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
        
        combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
        
        if combined_df.empty:
            return None
            
        analyzer = HashtagNetworkAnalyzer(combined_df)
        return analyzer.plot_hashtag_distribution()
    
    @lru_cache(maxsize=32)
    def get_mutual_stats(self, username):
        """
        Get mutual follower statistics for a specific user
        
        Args:
            username (str): Username to analyze
            
        Returns:
            dict: Statistics including:
                - mutual_followers: Number of mutual followers
                - total_followers: Total number of followers
                - total_following: Total number of following
                - mutual_percentage: Percentage of followers that are mutual
                - mutual_follower_usernames: List of mutual follower usernames
                
        Note:
            Results are cached using lru_cache for performance
        """
        outer_profile = self.data.get(username, {})
        profile_data = outer_profile.get(username, {})
        
        followers = profile_data.get('followers', {})
        following = profile_data.get('following', {})
        
        # Calculate statistics
        total_followers = len(followers)
        total_following = len(following)
        
        # Get mutual followers with their usernames
        mutual_followers_list = [
            follower['username']
            for follower in followers.values()
            if isinstance(follower, dict) 
            and 'username' in follower 
            and any(
                following_user['username'] == follower['username']
                for following_user in following.values()
                if isinstance(following_user, dict) and 'username' in following_user
            )
        ]
        
        mutual_count = len(mutual_followers_list)
        
        return {
            'mutual_followers': mutual_count,
            'total_followers': total_followers,
            'total_following': total_following,
            'mutual_percentage': round((mutual_count / total_followers * 100) if total_followers > 0 else 0, 2),
            'mutual_follower_usernames': mutual_followers_list
        }

    def filter_by_date(self, df, start_date=None, end_date=None):
        """
        Filter DataFrame by date range
        
        Args:
            df (pd.DataFrame): DataFrame to filter
            start_date (str, optional): Start date for filtering
            end_date (str, optional): End date for filtering
            
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        if df.empty:
            return df
        if start_date:
            df = df[df['date_posted'] >= start_date]
        if end_date:
            df = df[df['date_posted'] <= end_date]
        return df
    
    def filter_by_keywords(self, df, keywords):
        """
        Filter DataFrame by keywords in text
        
        Args:
            df (pd.DataFrame): DataFrame to filter
            keywords (list): List of keywords to search for
            
        Returns:
            pd.DataFrame: Filtered DataFrame containing only rows with matching keywords
        """
        if df.empty or not keywords:
            return df
        
        pattern = '|'.join(keywords)
        return df[df['text'].str.contains(pattern, case=False, na=False)]

    def archive_profiles(self, output_file):
        """
        Archive raw profile data with metadata
        
        Args:
            output_file (str): Path to archive file
            
        Note:
            - Updates existing archive if it exists
            - Adds metadata including timestamps and profile counts
            - Preserves first archived date if it exists
        """
        # First try to load existing archive
        existing_archive = {}
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_archive = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid JSON, start with empty archive
            pass

        # Create new archive data
        new_archive = {
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'total_profiles': len(self.data),
                'profile_usernames': list(self.data.keys())
            },
            'profiles': self.data
        }

        # If there's existing data, merge it
        if existing_archive:
            # Update existing profiles
            if 'profiles' in existing_archive:
                for username, profile_data in new_archive['profiles'].items():
                    existing_archive['profiles'][username] = profile_data
            else:
                existing_archive['profiles'] = new_archive['profiles']

            # Update metadata
            if 'metadata' in existing_archive:
                existing_archive['metadata'].update(new_archive['metadata'])
                # Keep track of first archived date if it exists
                if 'first_archived' in existing_archive['metadata']:
                    existing_archive['metadata']['last_updated'] = new_archive['metadata']['last_updated']
                else:
                    existing_archive['metadata']['first_archived'] = new_archive['metadata']['last_updated']
            else:
                existing_archive['metadata'] = new_archive['metadata']
                existing_archive['metadata']['first_archived'] = new_archive['metadata']['last_updated']

            new_archive = existing_archive

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(new_archive, f, ensure_ascii=False, indent=4)
            print(f"Successfully updated archive in {output_file}")
        except Exception as e:
            print(f"Error archiving profiles: {str(e)}")

    async def process_post_with_monitoring(self, post, username):
        """Process a single post and send alerts if necessary"""
        if self.keyword_monitor:
            metadata = {
                'username': username,
                'date_posted': post.get('date_posted', '').isoformat() if isinstance(post.get('date_posted'), datetime) else str(post.get('date_posted', '')),
                'likes': post.get('likes', 0),
                'replies': post.get('replies', 0)
            }
            await self.keyword_monitor.process_text(post.get('text', ''), metadata)

    async def process_and_archive(self, output_file, archive_file, keywords=None, start_date=None, end_date=None):
        """Process, filter and archive data with warning system integration"""
        empty_df = pd.DataFrame(columns=['username', 'text', 'date_posted', 'likes', 'replies', 'hashtags', 'hashtag_count'])
        
        all_posts_data = []
        profile_stats = {}
        
        for username, outer_profile in self.data.items():
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                profile_stats[username] = {
                    **self.get_mutual_stats(username),
                    'hashtag_stats': self.get_hashtag_stats(username)
                }
                
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
                    
                    # Process each post for monitoring
                    if self.keyword_monitor:
                        for _, post in posts_df.iterrows():
                            await self.process_post_with_monitoring(post.to_dict(), username)
        
        combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else empty_df
        filtered_df = self.filter_by_date(combined_df, start_date, end_date)
        filtered_df = self.filter_by_keywords(filtered_df, keywords)
        
        self.archive_profiles(archive_file)

        # Convert timestamps to strings before JSON serialization
        posts_dict = filtered_df.to_dict('records')
        for post in posts_dict:
            if isinstance(post.get('date_posted'), pd.Timestamp):
                post['date_posted'] = post['date_posted'].isoformat()

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
            'profile_stats': profile_stats,
            'posts': posts_dict
        }

        # Save the results
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"Successfully processed and saved results to {output_file}")
        except Exception as e:
            print(f"Error saving processed results: {str(e)}")
            
        return result