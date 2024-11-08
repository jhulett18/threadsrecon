import time
from scraping.scraper import ThreadsScraper
#from processing.data_processing import process_data
#from analysis.sentiment_analysis import analyze_sentiment
#from visualization.visualization import create_visualizations
#from reports.report_generator import generate_report

#call each module
def main():
    base_url = "https://www.threads.net"
     # Create an instance of ThreadsScraper
    scraper = ThreadsScraper(base_url)

    # Specify the username you want to fetch the profile for
    usernames = ["jonrettinger","ktla5news"]  # Example usernames

    for username in usernames:
        print(f"\nFetching profile for: {username}")
        profile_data = scraper.fetch_profile(username)
        
        if profile_data:
            print("Profile Data:", profile_data)
            if profile_data['bio'] == "Bio not found" and 'error_details' in profile_data:
                print("Debug Info:", profile_data['error_details'])
        else:
            print("No data retrieved.")
        
        # Add delay between requests to be respectful
        time.sleep(2)


if __name__ == "__main__":
    main()