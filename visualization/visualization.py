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