import time
from scraping.scraper import ThreadsScraper
#from processing.data_processing import process_data
#from analysis.sentiment_analysis import analyze_sentiment
#from visualization.visualization import create_visualizations
#from reports.report_generator import generate_report

#call each module
def main():
    base_url = "https://www.threads.net"
    scraper = ThreadsScraper(base_url)
    username = "everydaywoksoflife"
    profile_data = scraper.fetch_profile(username)
    
    if profile_data:
        print("Profile Data:", profile_data)
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    main()