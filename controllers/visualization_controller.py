#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller for the visualization functionality of Threads Recon Tool
"""

import os
import pandas as pd
from datetime import datetime
from visualization.visualization import HashtagNetworkAnalyzer
from analysis.sentiment_analysis import process_posts
from processing.data_processing import DataProcessor

def visualize_all(config):
    """
    Generate all visualizations from the processed data
    
    Args:
        config (dict): Configuration containing visualization settings
    
    Returns:
        dict: Dictionary containing paths to generated visualizations
    """
    processor = DataProcessor(config["AnalysisSettings"]["input_file"])
    
    # Get visualization directory from config
    viz_dir = config["AnalysisSettings"]["visualization_dir"]
    os.makedirs(viz_dir, exist_ok=True)
    
    # Process all posts data ONCE into a single DataFrame
    print("Processing posts data...")
    all_posts_data = []
    for username, outer_profile in processor.data.items():
        if isinstance(outer_profile, dict):
            inner_profile = outer_profile.get(username, {})
            posts = inner_profile.get('posts', {})
            if posts:
                posts_df = process_posts(posts)
                posts_df['username'] = username
                all_posts_data.append(posts_df)
    
    combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
    
    if combined_df.empty:
        print("No posts data found. Skipping visualizations.")
        return {}
    
    # Initialize analyzer ONCE with the combined data
    print(f"Initializing network analyzer with {len(combined_df)} posts...")
    analyzer = HashtagNetworkAnalyzer(combined_df)
    
    # Generate timestamp once
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate visualizations with progress reporting
    visualizations = {}
    visualization_paths = {}
    
    print("Generating hashtag network visualization...")
    try:
        visualizations['hashtag_network'] = analyzer.plot_plotly(min_edge_weight=1, min_node_freq=1, max_nodes=50)
        print("Hashtag network visualization generated successfully")
    except Exception as e:
        print(f"Error generating hashtag network: {str(e)}")
        visualizations['hashtag_network'] = None
    
    print("Generating sentiment trends visualization...")
    visualizations['sentiment'] = analyzer.plot_sentiment_trends(combined_df)
    
    print("Generating engagement metrics visualization...")
    visualizations['engagement'] = analyzer.plot_engagement_metrics(combined_df)
    
    print("Generating mutual followers network visualization...")
    visualizations['mutual_followers'] = analyzer.plot_mutual_followers_network(processor.data)
    
    print("Generating hashtag distribution visualization...")
    visualizations['hashtag_dist'] = analyzer.plot_hashtag_distribution()
    
    # Add debug output before saving
    for name, fig in visualizations.items():
        print(f"Visualization '{name}' is {'valid' if fig is not None else 'None'}")
        
    # Save visualizations with progress reporting
    for name, fig in visualizations.items():
        if fig:
            print(f"Saving {name} visualization...")
            
            # Save HTML for interactive viewing (faster)
            html_path = os.path.join(viz_dir, f"{name}_{timestamp}.html")
            fig.write_html(html_path)
            visualization_paths[f"{name}_html"] = html_path
            
            # Only save PNG if needed for report generation
            if config.get("ReportGeneration", {}).get("generate_report", True):
                png_path = os.path.join(viz_dir, f"{name}_{timestamp}.png")
                fig.write_image(png_path, scale=2)  # Higher resolution for better quality
                visualization_paths[f"{name}_png"] = png_path
    
    # Print strongest connections
    edge_weights = sorted(
        [(tags, weight) for tags, weight in analyzer.edge_weights.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    print("\nStrongest hashtag connections:")
    for (tag1, tag2), weight in edge_weights:
        print(f"#{tag1} - #{tag2}: {weight} co-occurrences")
        
    return visualization_paths 