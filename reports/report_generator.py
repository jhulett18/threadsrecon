import pdfkit
import json
import json2html
import os

class GenerateReport:
    def create_report(self, data, path):
        try:
            config = pdfkit.configuration(wkhtmltopdf=path)
            # First convert JSON to HTML
            with open(data, 'r') as f:
                data = json.load(f)
            
            # Create HTML content (example)
            html_content = f"""
            <html>
                <body>
                    <h1>Analysis Report</h1>
                    {self.json_to_html(data)}
                </body>
            </html>
            """
            temp_file = 'temp.html'

            # Save HTML content to a temporary file
            with open(temp_file, 'w') as f:
                f.write(html_content)
            
            # Convert HTML to PDF
            pdfkit.from_file(temp_file, 'out.pdf', configuration=config)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    def json_to_html(self, data):
        return json2html.json2html.convert(json=data)