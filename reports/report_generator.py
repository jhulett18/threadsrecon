"""
Report Generator Module

This module handles the generation of PDF reports from analyzed data and visualizations.
It combines JSON data with multiple visualization images into a formatted PDF document.
"""

import pdfkit
import json
import json2html
import os
import datetime
import base64

class GenerateReport:
    """
    A class to generate PDF reports from analyzed data and visualizations
    
    This class combines multiple data sources into a single PDF report:
    - JSON data from analysis results
    - Network visualization images
    - Sentiment analysis plots
    - Engagement metrics visualizations
    - Mutual followers network graphs
    - Hashtag distribution charts
    """

    def create_report(self, data, path, network_image_path, sentiment_image_path, 
                     engagement_image_path, mutual_followers_image_path, 
                     hashtag_distribution_image_path, output_path):
        """
        Create a comprehensive PDF report combining data and visualizations
        
        Args:
            data (str): Path to JSON file containing analysis results
            path (str): Path to wkhtmltopdf executable
            network_image_path (str): Path to hashtag network visualization
            sentiment_image_path (str): Path to sentiment analysis plot
            engagement_image_path (str): Path to engagement metrics visualization
            mutual_followers_image_path (str): Path to mutual followers network graph
            hashtag_distribution_image_path (str): Path to hashtag distribution chart
            output_path (str): Destination path for generated PDF
            
        Note:
            - Uses wkhtmltopdf for PDF generation
            - Converts images to base64 for HTML embedding
            - Applies consistent styling across the report
            - Handles missing images gracefully
        """
        try:
            # Initialize PDF configuration with wkhtmltopdf path
            config = pdfkit.configuration(wkhtmltopdf=path)
            
            # Load and parse JSON analysis data
            with open(data, 'r') as f:
                data = json.load(f)
            
            # Process each visualization image, converting to base64 if available
            image_sections = {
                'network': (network_image_path, ""),
                'sentiment': (sentiment_image_path, ""),
                'engagement': (engagement_image_path, ""),
                'mutual_followers': (mutual_followers_image_path, ""),
                'hashtag_distribution': (hashtag_distribution_image_path, "")
            }
            
            # Convert each image to base64 if it exists
            for section_name, (image_path, _) in image_sections.items():
                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        image_sections[section_name] = (
                            image_path,
                            f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%; height: auto;">'
                        )
            
            # Create HTML content with consistent styling
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    /* Global styles for consistent formatting */
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 40px;
                        color: #333;
                    }}
                    
                    /* Header styling */
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 30px;
                    }}
                    h2 {{
                        color: #34495e;
                        margin-top: 25px;
                    }}
                    
                    /* Table styling */
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f5f6fa;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    
                    /* Section styling */
                    .section {{
                        margin-bottom: 30px;
                        padding: 20px;
                        background: #fff;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }}
                    .highlight {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-left: 4px solid #3498db;
                        margin: 20px 0;
                    }}
                    
                    /* Image container styling */
                    .network-image {{
                        text-align: center;
                        margin: 20px 0;
                    }}
                    
                    /* Footer styling */
                    footer {{
                        margin-top: 50px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        text-align: center;
                        font-size: 0.9em;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <!-- Analysis Results Section -->
                <h1>Analysis Report</h1>
                <div class="section">
                    {self.json_to_html(data)}
                </div>
                
                <!-- Network Visualization Section -->
                <h1>Hashtag Network</h1>
                <div class="section network-image">
                    {image_sections['network'][1]}
                </div>
                
                <!-- Sentiment Analysis Section -->
                <h1>Sentiment Trends</h1>
                <div class="section sentiment-image">
                    {image_sections['sentiment'][1]}
                </div>
                
                <!-- Engagement Metrics Section -->
                <h1>Engagement Metrics</h1>
                <div class="section engagement-image">
                    {image_sections['engagement'][1]}
                </div>
                
                <!-- Mutual Followers Section -->
                <h1>Mutual Followers Network</h1>
                <div class="section mutual-followers-image">
                    {image_sections['mutual_followers'][1]}
                </div>
                
                <!-- Hashtag Distribution Section -->
                <h1>Hashtag Distribution</h1>
                <div class="section hashtag-distribution-image">
                    {image_sections['hashtag_distribution'][1]}
                </div>
                
                <!-- Report Footer -->
                <footer>
                    Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </footer>
            </body>
            </html>
            """
            
            # Create temporary HTML file
            temp_file = 'temp.html'
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Configure PDF generation options
            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
                'no-outline': None,
                'enable-local-file-access': None,
                'image-quality': 100  # Ensure high-quality image rendering
            }
            
            # Generate PDF from HTML
            pdfkit.from_file(temp_file, output_path, configuration=config, options=options)
            
        finally:
            # Clean up temporary HTML file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def json_to_html(self, data):
        """
        Convert JSON data to formatted HTML
        
        Args:
            data (dict): JSON data to convert
            
        Returns:
            str: Formatted HTML representation of the JSON data
            
        Note:
            Uses json2html library for conversion while maintaining
            consistent styling with the rest of the report
        """
        return json2html.json2html.convert(json=data)