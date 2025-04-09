# ThreadsRecon Project Structure

This document describes the modular structure of the ThreadsRecon codebase, designed to improve code organization, maintainability, and comprehension.

## Directory Structure

```
threadsrecon/
├── main.py                      # Main entry point
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── helpers.py               # Helper utilities
├── controllers/                 # Controller modules
│   ├── __init__.py
│   ├── scrape_controller.py     # Scraping functionality
│   ├── analysis_controller.py   # Data analysis functionality
│   ├── visualization_controller.py # Visualization generation
│   └── report_controller.py     # Report generation
├── scraping/                    # Scraping modules
│   ├── __init__.py
│   └── scraper.py               # Threads.net scraper
├── analysis/                    # Analysis modules
│   ├── __init__.py
│   └── sentiment_analysis.py    # Sentiment analysis utilities
├── processing/                  # Data processing modules
│   ├── __init__.py
│   └── data_processing.py       # Data processor
├── visualization/               # Visualization modules
│   ├── __init__.py
│   └── visualization.py         # Network visualization
├── reports/                     # Report generation modules
│   ├── __init__.py
│   └── report_generator.py      # PDF report generator
├── warningsys/                  # Warning system modules
│   └── warning_system.py        # Warning system implementation
├── config/                      # Configuration utilities
│   └── config_manager.py        # Configuration manager
├── data/                        # Data storage
│   ├── visualizations/          # Generated visualizations
│   └── reports/                 # Generated reports
└── settings.yaml                # Configuration file
```

## Module Descriptions

### Main Module

- **main.py**: The entry point of the application. It parses command-line arguments and orchestrates the execution of different components.

### Controllers

Controllers act as intermediaries between the main script and the actual implementation modules:

- **scrape_controller.py**: Handles the scraping process by coordinating the ThreadsScraper class.
- **analysis_controller.py**: Manages the data analysis process.
- **visualization_controller.py**: Controls the generation of various visualizations.
- **report_controller.py**: Handles report generation by integrating visualizations.

### Utilities

- **utils/helpers.py**: Contains general utility functions for configuration, setup, and UI elements.

### Implementation Modules

These modules contain the actual implementation logic:

- **scraping/scraper.py**: Implements web scraping functionality for Threads.net.
- **analysis/sentiment_analysis.py**: Implements sentiment analysis for posts.
- **processing/data_processing.py**: Handles data preprocessing and processing.
- **visualization/visualization.py**: Contains visualization classes and functions.
- **reports/report_generator.py**: Implements PDF report generation.
- **warningsys/warning_system.py**: Implements the warning notification system.
- **config/config_manager.py**: Handles configuration management.

## Data Flow

1. **Scraping**: The scraper collects data from Threads.net and saves it to JSON files.
2. **Analysis**: The data processor analyzes the scraped data for patterns and insights.
3. **Visualization**: The visualization module generates network graphs and charts.
4. **Reporting**: The report generator combines analysis results and visualizations into a PDF report.

## Benefits of This Structure

1. **Modularity**: Each component has a single responsibility.
2. **Maintainability**: Changes in one module don't affect others.
3. **Testability**: Each module can be tested independently.
4. **Comprehension**: Clear separation of concerns makes the code easier to understand.
5. **Extensibility**: New features can be added without modifying existing modules.

## Usage

The application supports the following commands:

```bash
python main.py scrape    # Scrape data from Threads.net
python main.py analyze   # Analyze the scraped data
python main.py visualize # Generate visualizations from the analysis
python main.py report    # Generate a PDF report
python main.py all       # Run the complete pipeline
```

Each command can be run independently, or the entire pipeline can be executed with the 'all' command. 