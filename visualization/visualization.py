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
        """
        self.posts_df = posts_df
        self.edge_weights = self._calculate_edge_weights()
        self.node_frequencies = self._calculate_node_frequencies()
        
    def _calculate_edge_weights(self):
        """Calculate how often hashtags appear together"""
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
        """Calculate how often each hashtag appears"""
        frequencies = defaultdict(int)
        
        for hashtags in self.posts_df['hashtags']:
            if isinstance(hashtags, list):
                for tag in hashtags:
                    frequencies[tag] += 1
                    
        return frequencies
    
    def create_network_graph(self, min_edge_weight=2, min_node_freq=3):
        """Create NetworkX graph with filtered edges and nodes"""
        G = nx.Graph()
        
        # Add edges that meet minimum weight threshold
        for (tag1, tag2), weight in self.edge_weights.items():
            if weight >= min_edge_weight:
                # Only add edge if both nodes meet frequency threshold
                if (self.node_frequencies[tag1] >= min_node_freq and 
                    self.node_frequencies[tag2] >= min_node_freq):
                    G.add_edge(tag1, tag2, weight=weight)
        
        return G
    
    def plot_matplotlib(self, min_edge_weight=2, min_node_freq=3, figsize=(12, 8)):
        """Create static visualization using matplotlib"""
        G = self.create_network_graph(min_edge_weight, min_node_freq)
        
        if len(G) == 0:
            print("No nodes meet the minimum criteria")
            return
        
        plt.figure(figsize=figsize)
        
        # Calculate layout
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G)), iterations=50)
        
        # Draw edges with varying thickness
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        max_weight = max(edge_weights)
        edge_widths = [2 * w/max_weight for w in edge_weights]
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3)
        
        # Draw nodes with varying sizes
        node_sizes = [100 * self.node_frequencies[node] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                             node_color='lightblue', alpha=0.6)
        
        # Add labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        plt.title("Hashtag Co-occurrence Network")
        plt.axis('off')
        return plt.gcf()
    
    def plot_plotly(self, min_edge_weight=2, min_node_freq=3):
        """Create interactive visualization using plotly"""
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
        """Visualize sentiment trends over time"""
        # Group by date and calculate average sentiment
        daily_sentiment = posts_df.groupby(posts_df['date_posted'].dt.date).agg({
            'compound': 'mean',
            'pos': 'mean',
            'neg': 'mean',
            'neu': 'mean'
        }).reset_index()
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_sentiment['date_posted'], daily_sentiment['compound'], 
                label='Compound', linewidth=2)
        ax.plot(daily_sentiment['date_posted'], daily_sentiment['pos'], 
                label='Positive', alpha=0.7)
        ax.plot(daily_sentiment['date_posted'], daily_sentiment['neg'], 
                label='Negative', alpha=0.7)
        
        plt.title('Sentiment Analysis Trends Over Time')
        plt.xlabel('Date')
        plt.ylabel('Sentiment Score')
        plt.legend()
        plt.xticks(rotation=45)
        return fig
    
    def plot_engagement_metrics(self, posts_df):
        """Visualize likes, replies, and reposts trends"""
        # Group by date and calculate engagement metrics
        daily_engagement = posts_df.groupby(posts_df['date_posted'].dt.date).agg({
            'likes': 'sum',
            'replies': 'sum',
            'reposts': 'sum'
        }).reset_index()
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Raw numbers
        ax1.plot(daily_engagement['date_posted'], daily_engagement['likes'], 
                label='Likes', marker='o')
        ax1.plot(daily_engagement['date_posted'], daily_engagement['replies'], 
                label='Replies', marker='s')
        ax1.plot(daily_engagement['date_posted'], daily_engagement['reposts'], 
                label='Reposts', marker='^')
        ax1.set_title('Daily Engagement Metrics')
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        
        # Stacked percentage
        engagement_pct = daily_engagement[['likes', 'replies', 'reposts']].div(
            daily_engagement[['likes', 'replies', 'reposts']].sum(axis=1), axis=0)
        engagement_pct.plot(kind='area', stacked=True, ax=ax2)
        ax2.set_title('Engagement Distribution Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Percentage')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_mutual_followers_network(self, data):
        """Visualize mutual followers relationships between users"""
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
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 10))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=1000, font_size=8, font_weight='bold')
        plt.title('Mutual Followers Network')
        return fig
    
    def plot_hashtag_distribution(self):
        """Visualize hashtag usage distribution"""
        # Sort hashtags by frequency
        sorted_tags = sorted(self.node_frequencies.items(), 
                            key=lambda x: x[1], reverse=True)
        tags, frequencies = zip(*sorted_tags[:20])  # Top 20 hashtags
        
        # Create bar plot
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(tags, frequencies)
        
        # Customize appearance
        plt.title('Top 20 Hashtags by Usage')
        plt.xlabel('Hashtags')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        return fig