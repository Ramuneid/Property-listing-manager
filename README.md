# Property Listing Manager

An automated Python scraper for collecting real estate auction listings from eaukcionai.lt, filtering them by selected Lithuanian districts, and saving clean CSV reports locally.

## Project Overview

This project was built to automate a repetitive property research task: checking active real estate auctions, collecting relevant listings, and keeping the results in a structured format.

The scraper collects active real estate auction listings from multiple categories, filters them by district, removes duplicates, and saves the final results into a CSV file. It also includes a Windows Task Scheduler helper so the scraper can run automatically every day.

## What It Does

- Scrapes active real estate auctions from eaukcionai.lt
- Collects listings from multiple real estate categories:
  - Land plots
  - Buildings
  - Apartments
  - Other real estate objects
- Scrapes all available result pages in each category
- Filters listings by target districts:
  - Molėtai district
  - Vilnius district
- Avoids false matches from street names, for example:
  - Keeps `Vilniaus r. sav. Mickūnų mstl. Gaidūnų g. 24`
  - Rejects `Ignalinos r. sav. Dūkšto m. Vilniaus g. 61`
- Removes duplicate listings
- Saves results to CSV
- Creates debug CSV files with unfiltered results for inspection
- Logs each run to a local log file
- Can be scheduled to run automatically every day at 10:00

## Skills Demonstrated

This project demonstrates practical Python automation and data-processing skills:

- Web scraping with `requests` and `BeautifulSoup`
- HTML parsing using CSS selectors
- Pagination handling across multiple result pages
- URL manipulation with `urllib.parse`
- Data cleaning and normalization
- District-based filtering logic
- Duplicate detection
- CSV file generation with UTF-8 encoding
- Logging and error handling
- Windows Task Scheduler automation
- Virtual environment and dependency management
- Project documentation and GitHub-ready repository structure

## Tech Stack

- Python 3
- requests
- BeautifulSoup
- schedule
- CSV files
- Windows Task Scheduler

## Project Structure

```text
Property listing manager/
├── Data/                            # Generated CSV files, ignored by Git
├── listing_collector.py             # Main scraper and CSV exporter
├── setup_scheduler.py               # Windows Task Scheduler helper
├── requirements.txt                 # Python dependencies
├── PRD_Property_Listing_Manager.md  # Product requirements document
├── README.md                        # Project documentation
└── venv/                            # Local virtual environment, ignored by Git
```

## CSV Output

The final CSV contains only the most useful fields:

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

The `collected_at` column is placed last so the main listing information stays easy to scan.

## Installation

Clone or download the project, then open the project folder:

```powershell
cd "C:\Users\maart\Documents\Property listing manager"
```

Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Usage

Run the scraper manually:

```powershell
python listing_collector.py
```

The scraper saves CSV files into:

```text
Data/
```

Typical generated files:

```text
YYYY-MM-DD_listings.csv
YYYY-MM-DD_HH-MM-SS_unfiltered_debug_listings.csv
```

## Scheduler

The project includes a helper script for Windows Task Scheduler.

Test the scraper through the scheduler helper:

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

By default, the task is configured to run every day at 10:00.

## Configuration

The main settings are at the top of `listing_collector.py`:

```python
TARGET_DISTRICTS = ["Molėtų", "Vilniaus"]
MAX_PAGES = 100
SAVE_UNFILTERED_DEBUG_CSV = True
```

The scheduled run time is configured in `setup_scheduler.py`:

```python
RUN_TIME = "10:00"
```

## Notes

Generated data, logs, and the local virtual environment should not be committed to GitHub. The included `.gitignore` excludes these local files.

This project is intended for learning, portfolio demonstration, and personal workflow automation. When scraping any website, always respect its terms of service and avoid excessive request rates.
