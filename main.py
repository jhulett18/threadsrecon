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
    usernames = ["everydaywoksoflife","ktla5news"] #Example usernames
    
    for username in usernames:
        profile_data = scraper.fetch_profile(username)

        if profile_data:
            print(f"Profile Data for {username}:",profile_data)
        else:
            print(f"No data retrieved for {username}.")
            
    scraper.driver.quit()
if __name__ == "__main__":
    main()