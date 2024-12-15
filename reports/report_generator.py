import pdfkit
import json
import json2html
import os
import datetime
import base64

class GenerateReport:
    def create_report(self, data, path, network_image_path):
        try:
            config = pdfkit.configuration(wkhtmltopdf=path)
            # Load JSON data
            with open(data, 'r') as f:
                data = json.load(f)
            
            # Convert network image to base64 (if it's a file)
            image_html = ""
            if network_image_path and os.path.exists(network_image_path):
                with open(network_image_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    image_html = f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%; height: auto;">'
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 40px;
                        color: #333;
                    }}
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
                    .network-image {{
                        text-align: center;
                        margin: 20px 0;
                    }}
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
                <h1>Analysis Report</h1>
                <div class="section">
                    {self.json_to_html(data)}
                </div>
                <h1>Hashtag Network</h1>
                <div class="section network-image">
                    {image_html}
                </div>
                <footer>
                    Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </footer>
            </body>
            </html>
            """
            temp_file = 'temp.html'

            # Save HTML content to a temporary file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
                'no-outline': None,
                'enable-local-file-access': None,
                'image-quality': 100
            }
            
            # Convert HTML to PDF
            pdfkit.from_file(temp_file, 'out.pdf', configuration=config, options=options)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def json_to_html(self, data):
        return json2html.json2html.convert(json=data)