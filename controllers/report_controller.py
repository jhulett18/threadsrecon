#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller for the report generation functionality of Threads Recon Tool
"""

import os
import glob
from datetime import datetime
from reports.report_generator import GenerateReport

def generate_report(config, visualization_paths=None):
    """
    Generate a PDF report with all analysis results
    
    Args:
        config (dict): Configuration containing report generation settings
        visualization_paths (dict, optional): Dictionary containing paths to visualizations.
                                            If None, will attempt to find most recent visualizations.
    
    Returns:
        str: Path to the generated report
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = config["ReportGeneration"]["output_path"]
    
    # Insert timestamp before the file extension
    base, ext = os.path.splitext(output_path)
    output_path_with_timestamp = f"{base}_{timestamp}{ext}"
    
    # Get the visualization directory from config
    viz_dir = config["AnalysisSettings"]["visualization_dir"]
    
    # If visualization paths are not provided, find the most recent files
    if not visualization_paths:
        # Find the most recent files for each visualization type
        network_plot = max(glob.glob(os.path.join(viz_dir, "hashtag_network_*.png")), default=None, key=os.path.getctime)
        sentiment_plot = max(glob.glob(os.path.join(viz_dir, "sentiment_*.png")), default=None, key=os.path.getctime)
        engagement_plot = max(glob.glob(os.path.join(viz_dir, "engagement_*.png")), default=None, key=os.path.getctime)
        mutual_followers_plot = max(glob.glob(os.path.join(viz_dir, "mutual_followers_*.png")), default=None, key=os.path.getctime)
        hashtag_dist_plot = max(glob.glob(os.path.join(viz_dir, "hashtag_dist_*.png")), default=None, key=os.path.getctime)
    else:
        # Use provided visualization paths
        network_plot = visualization_paths.get("hashtag_network_png")
        sentiment_plot = visualization_paths.get("sentiment_png")
        engagement_plot = visualization_paths.get("engagement_png")
        mutual_followers_plot = visualization_paths.get("mutual_followers_png")
        hashtag_dist_plot = visualization_paths.get("hashtag_dist_png")
    
    # Convert relative paths to absolute paths
    if network_plot:
        network_plot = os.path.abspath(network_plot)
    if sentiment_plot:
        sentiment_plot = os.path.abspath(sentiment_plot)
    if engagement_plot:
        engagement_plot = os.path.abspath(engagement_plot)
    if mutual_followers_plot:
        mutual_followers_plot = os.path.abspath(mutual_followers_plot)
    if hashtag_dist_plot:
        hashtag_dist_plot = os.path.abspath(hashtag_dist_plot)
    
    print(f"Generating report with visualizations:")
    print(f"- Network plot: {network_plot}")
    print(f"- Sentiment plot: {sentiment_plot}")
    print(f"- Engagement plot: {engagement_plot}")
    print(f"- Mutual followers plot: {mutual_followers_plot}")
    print(f"- Hashtag distribution plot: {hashtag_dist_plot}")
    
    report = GenerateReport()
    report.create_report(
        config["AnalysisSettings"]["output_file"],
        config["ReportGeneration"]["path_to_wkhtmltopdf"],
        network_plot,
        sentiment_plot,
        engagement_plot,
        mutual_followers_plot,
        hashtag_dist_plot,
        output_path_with_timestamp
    )
    
    print(f"Report generated successfully: {output_path_with_timestamp}")
    return output_path_with_timestamp 