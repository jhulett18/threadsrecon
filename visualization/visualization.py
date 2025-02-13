import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import defaultdict
import numpy as np

class HashtagNetworkAnalyzer:
    def __init__(self, posts_df):
        """
        Initialize analyzer with a DataFrame containing posts and their hashtags
        posts_df should have a 'hashtags' column containing lists of hashtags
        
        The class maintains two main data structures:
        - edge_weights: Dictionary tracking how often hashtag pairs appear together
        - node_frequencies: Dictionary tracking individual hashtag usage counts
        """
        self.posts_df = posts_df
        self.edge_weights = self._calculate_edge_weights()
        self.node_frequencies = self._calculate_node_frequencies()
        
    def _calculate_edge_weights(self):
        """
        Calculate how often hashtags appear together
        Creates edges between hashtags that appear in the same post
        Uses sorted tuples as keys to ensure consistent edge representation
        Returns: Dictionary with (hashtag1, hashtag2) tuples as keys and co-occurrence counts as values
        """
        edge_weights = defaultdict(int)
        
        for hashtags in self.posts_df['hashtags']:
            if isinstance(hashtags, list) and len(hashtags) > 1:
                # Create pairs of hashtags that appear together
                for i, tag1 in enumerate(hashtags):
                    for tag2 in hashtags[i+1:]:
                        # Sort tags to ensure consistent edge keys
                        edge = tuple(sorted([tag1, tag2]))
                        edge_weights[edge] += 1
                        
        return edge_weights
    
    def _calculate_node_frequencies(self):
        """
        Calculate how often each hashtag appears
        Counts individual hashtag occurrences across all posts
        Returns: Dictionary with hashtags as keys and their frequencies as values
        """
        frequencies = defaultdict(int)
        
        for hashtags in self.posts_df['hashtags']:
            if isinstance(hashtags, list):
                for tag in hashtags:
                    frequencies[tag] += 1
                    
        return frequencies
    
    def create_network_graph(self, min_edge_weight=2, min_node_freq=3):
        """
        Create NetworkX graph with filtered edges and nodes
        
        Parameters:
        - min_edge_weight: Minimum number of co-occurrences required to create an edge
        - min_node_freq: Minimum number of times a hashtag must appear to be included
        
        Returns: NetworkX Graph object with filtered nodes and weighted edges
        """
        G = nx.Graph()
        
        # Add edges that meet minimum weight threshold
        for (tag1, tag2), weight in self.edge_weights.items():
            if weight >= min_edge_weight:
                # Only add edge if both nodes meet frequency threshold
                if (self.node_frequencies[tag1] >= min_node_freq and 
                    self.node_frequencies[tag2] >= min_node_freq):
                    G.add_edge(tag1, tag2, weight=weight)
        
        return G
    
    
    def plot_plotly(self, min_edge_weight=2, min_node_freq=3):
        """
        Create interactive visualization using plotly
        
        Features:
        - Interactive hovering with hashtag frequency information
        - Draggable nodes
        - Zoomable and pannable interface
        - Color gradient representing hashtag frequency
        - Customizable node sizes based on frequency
        
        Technical details:
        - Uses spring layout for initial node positioning
        - Creates separate traces for edges and nodes
        - Implements custom hover text formatting
        - Includes color scale for frequency visualization
        
        Returns: Plotly Figure object or None if no nodes meet criteria
        """
        G = self.create_network_graph(min_edge_weight, min_node_freq)
        
        if len(G) == 0:
            print("No nodes meet the minimum criteria")
            return
        
        # Calculate layout
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G)), iterations=50)
        
        # Create edge trace
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(G[edge[0]][edge[1]]['weight'])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_sizes = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            freq = self.node_frequencies[node]
            node_text.append(f"#{node}<br>Used {freq} times")
            node_sizes.append(freq)
            
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=True,
                size=[20 * (s/max(node_sizes)) for s in node_sizes],
                color=node_sizes,
                colorscale='YlOrRd',
                reversescale=True,
                colorbar=dict(
                    title='Usage Frequency',
                    thickness=15,
                    xanchor='left',
                    titleside='right'
                )
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Interactive Hashtag Network',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        return fig
    
    def plot_sentiment_trends(self, posts_df):
        """Visualize sentiment trends over time using Plotly"""
        # Group by date and calculate average sentiment
        daily_sentiment = posts_df.groupby(posts_df['date_posted'].dt.date).agg({
            'compound': 'mean',
            'pos': 'mean',
            'neg': 'mean',
            'neu': 'mean'
        }).reset_index()
        
        # Create the plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_sentiment['date_posted'],
            y=daily_sentiment['compound'],
            name='Compound',
            line=dict(width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_sentiment['date_posted'],
            y=daily_sentiment['pos'],
            name='Positive',
            line=dict(width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_sentiment['date_posted'],
            y=daily_sentiment['neg'],
            name='Negative',
            line=dict(width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Sentiment Analysis Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Sentiment Score',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_engagement_metrics(self, posts_df):
        """Visualize likes, replies, and reposts trends using Plotly"""
        # Group by date and calculate engagement metrics
        daily_engagement = posts_df.groupby(posts_df['date_posted'].dt.date).agg({
            'likes': 'sum',
            'replies': 'sum',
            'reposts': 'sum'
        }).reset_index()
        
        # Create subplots
        fig = go.Figure()
        
        # Raw numbers
        fig.add_trace(go.Scatter(
            x=daily_engagement['date_posted'],
            y=daily_engagement['likes'],
            name='Likes',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_engagement['date_posted'],
            y=daily_engagement['replies'],
            name='Replies',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_engagement['date_posted'],
            y=daily_engagement['reposts'],
            name='Reposts',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Daily Engagement Metrics',
            xaxis_title='Date',
            yaxis_title='Count',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_mutual_followers_network(self, data):
        """Visualize mutual followers relationships using Plotly"""
        G = nx.Graph()
        
        # Add nodes and edges
        for username, profile_data in data.items():
            G.add_node(username)
            profile = profile_data.get(username, {})
            followers = profile.get('followers', {})
            following = profile.get('following', {})
            
            # Add edges for mutual followers
            for follower in followers.values():
                follower_username = follower.get('username')
                if any(f.get('username') == follower_username for f in following.values()):
                    G.add_edge(username, follower_username)
        
        # Calculate layout
        pos = nx.spring_layout(G)
        
        # Create edge trace
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=20,
                color='lightblue',
                line=dict(width=2)
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Mutual Followers Network',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        return fig
    
    def plot_hashtag_distribution(self):
        """Visualize hashtag distribution using Plotly"""
        # Sort hashtags by frequency
        sorted_tags = sorted(self.node_frequencies.items(), 
                            key=lambda x: x[1], reverse=True)
        tags, frequencies = zip(*sorted_tags[:20])  # Top 20 hashtags
        
        # Create bar plot
        fig = go.Figure(data=[
            go.Bar(
                x=tags,
                y=frequencies,
                text=frequencies,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Top 20 Hashtags by Usage',
            xaxis_title='Hashtags',
            yaxis_title='Frequency',
            xaxis_tickangle=-45,
            showlegend=False,
            hovermode='x'
        )
        
        return fig