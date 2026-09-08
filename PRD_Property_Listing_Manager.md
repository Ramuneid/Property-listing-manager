# Product Requirements Document (PRD)

## Property Listing Manager

### 1. Project Overview

**Project name:** Property Listing Manager  
**Version:** 1.0  
**Created:** 2026-03-13  
**Original author:** Ramune Idzelyte  
**Project location:** `C:\Users\maart\Documents\Property listing manager`

### 2. Goal and Vision

Build an automated local system that collects the latest land/property listings from evarzytynes.lt every morning, filters them by selected districts, stores the results in CSV format, and makes the listings easy to review, manage, and export.

The first target category is land plots from evarzytynes.lt. The first target districts are Molėtai district and Vilnius district.

### 3. Core Features

#### 3.1 Automatic Listing Collection

- **Schedule:** Every day at 08:00
- **Source:** evarzytynes.lt
- **Category:** Land plots
- **Filters:** Molėtai district and Vilnius district
- **Data format:** CSV
- **Storage location:** `C:\Users\maart\Documents\Property listing manager\Data`
- **Main script:** `listing_collector.py`
- **Scheduler script:** `setup_scheduler.py`

#### 3.2 Collected Listing Data

Each collected listing should include:

- Listing ID
- Title
- Price
- Listing expiration date
- Location or district
- Description
- Number of photos
- Listing URL
- Collection date and time
- Listing status: relevant or irrelevant
- Source website

#### 3.3 Web Interface

The project may include a web interface for reviewing and managing collected listings.

Expected features:

- View collected listings
- Change listing status between relevant and irrelevant
- Filter by date, price, source, district, and status
- Search by title or description
- Download listing data as CSV

### 4. Technical Requirements

#### 4.1 Python Collector

- **Programming language:** Python 3.9+
- **Dependency file:** `requirements.txt`
- **Recommended libraries:**
  - `requests` for HTTP requests
  - `beautifulsoup4` for HTML parsing
  - `pandas` for CSV handling
  - `schedule` for local scheduling support
  - `logging` for logs and diagnostics
- **Automatic execution:** Windows Task Scheduler

#### 4.2 Web Interface

- **Possible technologies:** HTML, CSS, JavaScript, and Python Flask
- **Data storage:** CSV files in the local `Data` folder
- **Expected functionality:**
  - Dynamic listing display
  - Status editing
  - Filtering and search
  - CSV download

#### 4.3 Project File Structure

Current project structure:

```yaml
Property listing manager/
├── Data/
├── listing_collector.py
├── setup_scheduler.py
├── requirements.txt
├── README.md
├── PRD_Property_Listing_Manager.md
└── venv/
```

Planned structure after adding a web interface:

```yaml
Property listing manager/
├── Data/
│   ├── 2026-03-13_listings.csv
│   ├── 2026-03-14_listings.csv
│   └── ...
├── web/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── server.py
├── listing_collector.py
├── setup_scheduler.py
├── requirements.txt
├── README.md
└── PRD_Property_Listing_Manager.md
```

### 5. User Scenarios

#### 5.1 Automatic Collection

1. Windows Task Scheduler starts the Python collector at 08:00.
2. `listing_collector.py` connects to evarzytynes.lt.
3. The collector searches the land plot category.
4. Listings are filtered by Molėtai district and Vilnius district.
5. The collected data is saved to a date-based CSV file in the `Data` folder.
6. The system writes a log entry with the collection result.

#### 5.2 Listing Review

1. The user opens the web interface.
2. The latest collected listings are displayed.
3. The user marks listings as relevant or irrelevant.
4. The user filters or searches listings.
5. The user downloads selected data as a CSV file.

### 6. Security Requirements

- Keep listing data stored locally unless external storage is explicitly added.
- Avoid hard-coded passwords, tokens, or API keys.
- Add logging for successful runs and errors.
- Handle connection, parsing, and file-writing errors safely.
- Keep backup copies of important collected data.
- Respect the terms of service and usage limits of listing websites.

### 7. Testing

#### 7.1 Unit Tests

- Test CSV file creation.
- Test listing data normalization.
- Test district filtering.
- Test duplicate detection.
- Test status updates.

#### 7.2 Integration Tests

- Test a full listing collection run.
- Test scheduled execution through Windows Task Scheduler.
- Test data integrity across multiple CSV files.
- Test web interface reading from the `Data` folder.

### 8. Deployment

#### 8.1 Requirements

- Python 3.9+
- Internet access
- Windows Task Scheduler access
- Write permissions for `C:\Users\maart\Documents\Property listing manager`

#### 8.2 Setup Steps

1. Open the project folder:

   ```bash
   cd "C:\Users\maart\Documents\Property listing manager"
   ```

2. Create or activate the virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure `listing_collector.py`.
5. Configure `setup_scheduler.py`.
6. Run a manual collection test:

   ```bash
   python listing_collector.py
   ```

7. Set up automatic collection:

   ```bash
   python setup_scheduler.py setup
   ```

8. Start the web server after the web interface is implemented.

### 9. Maintenance and Future Development

#### 9.1 Future Plans

- Add more evarzytynes.lt listing categories.
- Add email notifications for new listings.
- Add duplicate detection across collection runs.
- Add analytics for price, location, and listing trends.
- Add a mobile-friendly web interface.
- Add SQLite storage if CSV files become limiting.

#### 9.2 Maintenance

- Review logs regularly.
- Update selectors if evarzytynes.lt changes its page structure.
- Fix collection or parsing errors.
- Keep dependencies updated.
- Monitor scheduled task reliability.
