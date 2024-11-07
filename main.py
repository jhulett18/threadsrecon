from scraping.scraper import scrape_user_data
from processing.data_processing import process_data
from analysis.sentiment_analysis import analyze_sentiment
from visualization.visualization import create_visualizations
from reports.report_generator import generate_report

#call each module
def main():
    scraper = ThreadsScraper("https://threads.net")
    #implement other modules


if __name__ == "__main__":
    main()