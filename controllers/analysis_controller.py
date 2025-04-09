#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller for the analysis functionality of Threads Recon Tool
"""

from processing.data_processing import DataProcessor

async def analyze_data(config):
    """
    Handle the analysis functionality with warning system integration
    
    Args:
        config (dict): Configuration containing analysis settings and warning system credentials
    
    Features:
    - Integrates with Telegram warning system
    - Processes data based on configured date range
    - Archives processed data
    - Reports processing statistics
    
    Returns:
        None, but prints processing results
    """
    # Get Telegram credentials from config
    telegram_token = config.get("WarningSystem", {}).get("token")
    chat_id = config.get("WarningSystem", {}).get("chat_id")
    priority_keywords = config.get("WarningSystem", {}).get("priority_keywords", {
        'HIGH': ['urgent', 'emergency'],
        'MEDIUM': ['important', 'attention'],
        'LOW': ['update', 'info']
    })

    # Get analysis settings with defaults
    analysis_settings = config.get("AnalysisSettings", {})
    date_range = analysis_settings.get("date_range", {})
    
    # Initialize DataProcessor with warning system
    processor = DataProcessor(
        analysis_settings.get("input_file"),
        telegram_token=telegram_token,
        chat_id=chat_id,
        priority_keywords=priority_keywords
    )
    
    result = await processor.process_and_archive(
        analysis_settings.get("output_file"),
        analysis_settings.get("archive_file"),
        analysis_settings.get("keywords"),
        date_range.get("start"),
        date_range.get("end")
    )
    
    if result:
        print(f"Processing complete. Processed {result['metadata']['total_posts']} posts.")
    else:
        print("No data to process.")
        
    return result 