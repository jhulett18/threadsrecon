import json
from datetime import datetime
import pandas as pd
from analysis.sentiment_analysis import process_posts
from visualization.visualization import HashtagNetworkAnalyzer 

class DataProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = self.load_data()
        self.add_mutual_follower_status()

    def load_data(self):
        """Load JSON data from file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Input file {self.input_file} not found. Creating empty data structure.")
            return {}

    def add_mutual_follower_status(self):
        """Add is_mutual field to followers/following data"""
        for username, outer_profile in self.data.items():
            # Handle the double nesting
            profile_data = outer_profile.get(username, {})
            
            if isinstance(profile_data, dict):
                followers = profile_data.get('followers', {})
                following = profile_data.get('following', {})
                
                # Extract actual usernames from the nested structure
                follower_usernames = {v['username'] for k, v in followers.items() if isinstance(v, dict) and 'username' in v}
                following_usernames = {v['username'] for k, v in following.items() if isinstance(v, dict) and 'username' in v}
                
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
                
    def get_hashtag_stats(self, username=None):
        """Get hashtag statistics"""
        all_posts_data = []
        
        if username:
            outer_profile = self.data.get(username, {})
            if isinstance(outer_profile, dict):
                inner_profile = outer_profile.get(username, {})
                posts = inner_profile.get('posts', {})
                if posts:
                    posts_df = process_posts(posts)
                    posts_df['username'] = username
                    all_posts_data.append(posts_df)
        else:
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
        
        # Explode the hashtags list to analyze individual hashtags
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
    def get_mutual_stats(self, username):
        """Get mutual follower statistics for a profile"""
        outer_profile = self.data.get(username, {})
        profile_data = outer_profile.get(username, {})
        
        followers = profile_data.get('followers', {})
        following = profile_data.get('following', {})
        
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
        total_followers = len(followers)
        total_following = len(following)
        
        return {
            'mutual_followers': mutual_count,
            'total_followers': total_followers,
            'total_following': total_following,
            'mutual_percentage': round((mutual_count / total_followers * 100) if total_followers > 0 else 0, 2),
            'mutual_follower_usernames': mutual_followers_list  # Added this line
        }

    def filter_by_date(self, df, start_date=None, end_date=None):
        """Filter DataFrame by date range"""
        if df.empty:
            return df
        if start_date:
            df = df[df['date_posted'] >= start_date]
        if end_date:
            df = df[df['date_posted'] <= end_date]
        return df
    
    def filter_by_keywords(self, df, keywords):
        """Filter DataFrame by keywords in text"""
        if df.empty or not keywords:
            return df
        
        pattern = '|'.join(keywords)
        return df[df['text'].str.contains(pattern, case=False, na=False)]

    def archive_profiles(self, output_file):
        """Archive raw profile data with metadata by updating existing archive"""
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

    def process_and_archive(self, output_file, archive_file, keywords=None, start_date=None, end_date=None):
        """Process, filter and archive data"""
        empty_df = pd.DataFrame(columns=['username', 'text', 'date_posted', 'likes', 'replies','hashtags','hashtag_count'])
        
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
        # Try to load existing output file
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_result = json.load(f)
                # Update existing result with new data
                if isinstance(existing_result, dict):
                    # Merge posts
                    if 'posts' in existing_result:
                        existing_posts = existing_result['posts']
                        new_posts = result['posts']
                        # Create a set of existing post IDs or some unique identifier
                        existing_ids = {(post.get('username'), post.get('date_posted')) 
                                    for post in existing_posts}
                        # Only add posts that don't already exist
                        for post in new_posts:
                            if (post.get('username'), post.get('date_posted')) not in existing_ids:
                                existing_posts.append(post)
                        result['posts'] = existing_posts

                    # Update profile stats
                    if 'profile_stats' in existing_result:
                        existing_result['profile_stats'].update(result['profile_stats'])
                        result['profile_stats'] = existing_result['profile_stats']

                    # Update metadata
                    result['metadata']['last_updated'] = datetime.now().isoformat()
                    if 'metadata' in existing_result and 'first_processed' in existing_result['metadata']:
                        result['metadata']['first_processed'] = existing_result['metadata']['first_processed']
                    else:
                        result['metadata']['first_processed'] = result['metadata']['processed_date']
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid JSON, use new result as is
            result['metadata']['first_processed'] = result['metadata']['processed_date']

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"Successfully processed and saved results to {output_file}")
        except Exception as e:
            print(f"Error saving processed results: {str(e)}")
            
        return result