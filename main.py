import json
from datetime import datetime
from scraping.scraper import ThreadsScraper
#from processing.data_processing import process_data
#from analysis.sentiment_analysis import analyze_sentiment
#from visualization.visualization import create_visualizations
#from reports.report_generator import generate_report

#call each module
def datetime_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converts to "YYYY-MM-DDTHH:MM:SS" format
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    
def main():
    base_url = "https://www.threads.net"
    scraper = ThreadsScraper(base_url)
    usernames = ["everydaywoksoflife","ktla5news"] #Example usernames
    
    all_profiles_data = {}

    for username in usernames:
        profile_data = scraper.fetch_profile(username)

        if profile_data:
            print(f"Profile Data for {username}:",profile_data)
            all_profiles_data[username] = profile_data
        else:
            print(f"No data retrieved for {username}.")
    
    #write to JSON file
    with open("profiles_data.json", "w") as json_file:
        json.dump(all_profiles_data, json_file, indent=4, default=datetime_converter)
    
    scraper.driver.quit()
if __name__ == "__main__":
    main()