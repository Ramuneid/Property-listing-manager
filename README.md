# Property Listing Manager

A Python automation project that collects real estate auction listings from eaukcionai.lt, filters them by selected Lithuanian districts, and saves the results into clean CSV reports.

## Project Summary

Property Listing Manager was created to automate the process of checking active real estate auctions. Instead of manually opening auction categories, going through pages, checking locations, and copying listing data, this scraper performs the process automatically.

The project collects listings from several real estate categories, filters them by district, removes duplicates, and exports the final dataset into CSV format. It also includes Windows Task Scheduler integration so the scraper can run automatically every day at 10:00 AM.

## Main Features

- Scrapes real estate auction listings from eaukcionai.lt
- Collects data from multiple categories:
  - Land plots
  - Buildings
  - Apartments
  - Other real estate objects
- Handles pagination across all available result pages
- Filters listings by selected districts:
  - Molėtai district
  - Vilnius district
- Uses precise location filtering to avoid false matches from street names
- Removes duplicate listings
- Saves structured CSV reports
- Creates optional debug CSV files with unfiltered data
- Logs scraper activity and errors
- Supports automatic daily execution with Windows Task Scheduler

## Skills Demonstrated

### Python Programming

This project demonstrates core Python skills, including:

- Writing modular Python code
- Using functions and classes
- Working with file paths using `pathlib`
- Handling errors with `try` / `except`
- Working with dates and timestamps
- Reading and writing CSV files
- Cleaning and transforming text data
- Structuring a script for both manual and scheduled execution

### Web Scraping

The scraper uses `requests` and `BeautifulSoup` to collect data from public web pages.

Implemented web scraping skills include:

- Sending HTTP requests with browser-like headers
- Parsing HTML with BeautifulSoup
- Selecting elements with CSS selectors
- Extracting listing IDs, titles, prices, dates, locations, URLs, statuses, and categories
- Handling relative URLs and converting them into full URLs
- Scraping multiple pages using pagination
- Scraping several category URLs with shared parsing logic
- Building safer filters based on website data structure

### Automation

The project includes automation through Windows Task Scheduler.

Automation skills demonstrated:

- Creating scheduled tasks from Python
- Running the scraper automatically every day
- Configuring task time from code
- Running, listing, testing, and deleting scheduled tasks
- Separating manual script execution from automated execution
- Logging each run for monitoring and troubleshooting

## Tech Stack

- Python 3
- requests
- BeautifulSoup
- schedule
- csv
- pathlib
- logging
- Windows Task Scheduler

## How It Works

1. The scraper opens each configured eaukcionai.lt category URL.
2. It loops through all available pages in that category.
3. It extracts listing information from each auction card.
4. It combines listings from all categories.
5. It removes duplicate listings.
6. It filters listings by district.
7. It saves the final results into a CSV file.
8. It logs the collection process.
9. Windows Task Scheduler can run the script automatically every day at 10:00 AM.

## Categories Scraped

The scraper collects active listings from these real estate categories:

| Category | Website Filter |
|---|---|
| Land plots | `estateSubtype=1` |
| Buildings | `estateSubtype=2` |
| Apartments | `estateSubtype=3` |
| Other real estate objects | `estateSubtype=4` |

## Location Filtering

The filter is designed to avoid incorrect matches.

For example, this is accepted because the location starts with Vilnius district:

```text
Vilniaus r. sav. Mickūnų mstl. Gaidūnų g. 24
```

This is rejected because Vilnius appears only as a street name:

```text
Ignalinos r. sav. Dūkšto m. Vilniaus g. 61
```

## CSV Output

The final CSV contains:

```text
listing_id
title
price
expiration_date
location
url
auction_status
category
collected_at
```

Example output file:

```text
Data/2026-09-08_listings.csv
```

## Project Structure

```text
Property listing manager/
├── Data/                            # Generated CSV files
├── listing_collector.py             # Main scraper
├── setup_scheduler.py               # Windows Task Scheduler helper
├── requirements.txt                 # Python dependencies
├── PRD_Property_Listing_Manager.md  # Product requirements document
├── README.md                        # Project documentation
└── .gitignore                       # Files excluded from GitHub
```

## Installation

Clone the repository:

```powershell
git clone https://github.com/Ramuneid/Property-listing-manager.git
cd Property-listing-manager
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Manual Usage

Run the scraper manually:

```powershell
python listing_collector.py
```

The CSV files will be saved in:

```text
Data/
```

## Scheduler Usage

Test the collector:

```powershell
python setup_scheduler.py test
```

Create or update the scheduled task:

```powershell
python setup_scheduler.py setup
```

List the scheduled task:

```powershell
python setup_scheduler.py list
```

Run the scheduled task immediately:

```powershell
python setup_scheduler.py run
```

Delete the scheduled task:

```powershell
python setup_scheduler.py delete
```

By default, the scraper is scheduled to run every day at:

```text
10:00 AM
```

## Configuration

Main scraper settings are located near the top of `listing_collector.py`:

```python
TARGET_DISTRICTS = ["Molėtų", "Vilniaus"]
MAX_PAGES = 100
SAVE_UNFILTERED_DEBUG_CSV = True
```

Scheduler time is configured in `setup_scheduler.py`:

```python
RUN_TIME = "10:00"
```

## What I Learned

While building this project, I practiced:

- Turning a manual workflow into an automated Python process
- Understanding website HTML structure
- Extracting useful information from semi-structured web pages
- Handling pagination and duplicate records
- Designing filters that avoid incorrect matches
- Saving clean data for later analysis
- Creating an automated scheduled workflow on Windows
- Preparing a project for GitHub with documentation and `.gitignore`

## Notes

Generated CSV files, logs, and the local virtual environment are excluded from GitHub using `.gitignore`.

This project is intended for learning, portfolio demonstration, and personal workflow automation. When scraping websites, always respect their terms of service and avoid excessive request rates.
