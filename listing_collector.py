#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Property Listing Manager

Collects land/property auction listings from eaukcionai.lt, filters them by
target districts, and saves the results into a local CSV file.
"""

import csv
import logging
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests
import schedule
from bs4 import BeautifulSoup


# Main project folder.
BASE_DIR = Path(r"C:\Users\maart\Documents\Property listing manager")

# Folder where CSV files will be saved.
DATA_DIR = BASE_DIR / "Data"

# Log file path.
LOG_FILE = BASE_DIR / "listing_collector.log"

# Website settings.
SOURCE_NAME = "eaukcionai.lt"
BASE_URL = "https://www.eaukcionai.lt"

# Published and active real estate auction categories.
AUCTION_CATEGORIES = [
    {
        "name": "Land plots",
        "url": (
            "https://www.eaukcionai.lt/evs/pages/auctions.do"
            "?listType=1"
            "&page=0"
            "&estateType=1"
            "&estateSubtype=1"
            "&stateType=PASKELBTA-IR-VYKSTA"
        ),
    },
    {
        "name": "Buildings",
        "url": (
            "https://www.eaukcionai.lt/evs/pages/auctions.do"
            "?listType=1"
            "&page=0"
            "&estateType=1"
            "&estateSubtype=2"
            "&stateType=PASKELBTA-IR-VYKSTA"
        ),
    },
    {
        "name": "Apartments",
        "url": (
            "https://www.eaukcionai.lt/evs/pages/auctions.do"
            "?listType=1"
            "&page=0"
            "&estateType=1"
            "&estateSubtype=3"
            "&stateType=PASKELBTA-IR-VYKSTA"
        ),
    },
    {
        "name": "Other real estate objects",
        "url": (
            "https://www.eaukcionai.lt/evs/pages/auctions.do"
            "?listType=1"
            "&page=0"
            "&estateType=1"
            "&estateSubtype=4"
            "&stateType=PASKELBTA-IR-VYKSTA"
        ),
    },
]

# Districts we want to keep.
TARGET_DISTRICTS = ["Molėtų", "Vilniaus"]

# Set to True if you want a demo CSV even when the website blocks requests
# or when selectors need updating.
USE_TEST_DATA_WHEN_EMPTY = True

# Set to True to save a separate debug CSV with every listing before district
# filtering. This helps confirm what locations the website is returning.
SAVE_UNFILTERED_DEBUG_CSV = True

# Safety limit for pagination. Increase this if the website has more pages.
MAX_PAGES = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# Create folders before logging starts.
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


class ListingCollector:
    """Collects, filters, and saves property listings."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.listings = []

    def clean_text(self, value):
        """Convert messy website text into a clean single-line string."""
        if not value:
            return ""

        return " ".join(str(value).replace("\xa0", " ").split())

    def parse_price(self, price_text):
        """Extract a numeric price from text such as '14 000 Eur'."""
        if not price_text:
            return None

        price_clean = self.clean_text(price_text)
        price_clean = re.sub(r"[^\d,.]", "", price_clean)

        if not price_clean:
            return None

        try:
            return float(price_clean.replace(",", "."))
        except ValueError:
            logging.warning("Could not parse price: %s", price_text)
            return None

    def parse_date(self, date_text):
        """Extract a normalized date from text."""
        if not date_text:
            return ""

        date_text = self.clean_text(date_text)

        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
        ]

        for date_format in formats:
            try:
                return datetime.strptime(date_text, date_format).strftime(
                    "%Y-%m-%d %H:%M"
                )
            except ValueError:
                continue

        return date_text

    def fetch_page(self, url):
        """Download HTML from the auction website."""
        logging.info("Downloading page: %s", url)

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        return response.text

    def build_page_url(self, category_url, page_number):
        """Return the listings URL with the requested page number."""
        parsed_url = urlparse(category_url)
        query_params = parse_qs(parsed_url.query)
        query_params["page"] = [str(page_number)]

        updated_query = urlencode(query_params, doseq=True)

        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                updated_query,
                parsed_url.fragment,
            )
        )

    def extract_listing_id(self, link_element):
        """Extract listing number from URL query or text like 'Nr. 335497'."""
        if not link_element:
            return ""

        href = link_element.get("href", "")
        query_params = parse_qs(urlparse(href).query)

        if query_params.get("number"):
            return query_params["number"][0]

        text = self.clean_text(link_element.get_text())
        match = re.search(r"\d+", text)

        return match.group(0) if match else ""

    def extract_detail_value(self, card, label_text):
        """
        Extract values from rows such as:
        'Pabaiga: 2026-09-09 09:00'
        'Pradinė kaina: 14 000 Eur'
        """
        for item in card.select("ul.desc > li"):
            label = item.select_one(".txt")

            if not label:
                continue

            label_value = self.clean_text(label.get_text())

            if label_text.lower() not in label_value.lower():
                continue

            full_text = self.clean_text(item.get_text(" "))
            value = full_text.replace(label_value, "", 1)

            return self.clean_text(value)

        return ""

    def parse_listing_card(self, card, category_name):
        """Parse one auction listing card into a dictionary."""
        number_link = card.select_one("h2.no a")
        detail_link = number_link or card.select_one("a[href*='auction.do']")

        relative_url = detail_link.get("href", "") if detail_link else ""
        full_url = urljoin(BASE_URL, relative_url)

        title_element = card.select_one(".list_box ul.list > li")
        title = (
            self.clean_text(title_element.get_text(" ", strip=True))
            if title_element
            else ""
        )

        location_element = card.select_one(".list_box span.small")
        location = (
            self.clean_text(location_element.get_text())
            if location_element
            else ""
        )

        auction_status_element = card.select_one(".label.label-primary")
        auction_status = (
            self.clean_text(auction_status_element.get_text())
            if auction_status_element
            else ""
        )

        price_text = self.extract_detail_value(card, "Pradinė kaina")
        expiration_text = self.extract_detail_value(card, "Pabaiga")

        return {
            "listing_id": self.extract_listing_id(number_link),
            "title": title,
            "price": self.parse_price(price_text),
            "expiration_date": self.parse_date(expiration_text),
            "location": location,
            "url": full_url,
            "auction_status": auction_status,
            "category": category_name,
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def parse_listings(self, html, category_name):
        """Parse all listing cards from the downloaded HTML page."""
        soup = BeautifulSoup(html, "html.parser")

        try:
            listing_cards = soup.select("li:has(h2.no):has(ul.desc):has(.list_box)")
        except Exception:
            listing_cards = []

        if not listing_cards:
            listing_cards = [
                item
                for item in soup.select("li")
                if item.select_one("h2.no")
                and item.select_one("ul.desc")
                and item.select_one(".list_box")
            ]

        parsed_listings = []

        for card in listing_cards:
            listing = self.parse_listing_card(card, category_name)

            if listing["listing_id"] or listing["title"] or listing["url"]:
                parsed_listings.append(listing)

        logging.info("Parsed %s listings before filtering", len(parsed_listings))
        return parsed_listings

    def scrape_category_pages(self, category):
        """Scrape every available result page for one category."""
        all_listings = []
        seen_page_signatures = set()
        category_name = category["name"]
        category_url = category["url"]

        logging.info("Scraping category: %s", category_name)
        print(f"Scraping category: {category_name}")

        for page_number in range(MAX_PAGES):
            page_url = self.build_page_url(category_url, page_number)
            html = self.fetch_page(page_url)
            page_listings = self.parse_listings(html, category_name)

            if not page_listings:
                logging.info(
                    "Stopping %s at page %s: no listings found",
                    category_name,
                    page_number,
                )
                break

            page_keys = tuple(
                f"{category_name}:{listing.get('listing_id') or listing.get('url')}"
                for listing in page_listings
            )

            if page_keys in seen_page_signatures:
                logging.info(
                    "Stopping %s at page %s: page repeated previous results",
                    category_name,
                    page_number,
                )
                break

            seen_page_signatures.add(page_keys)
            all_listings.extend(page_listings)

            print(
                f"Parsed {category_name}, page {page_number}: "
                f"{len(page_listings)} listings"
            )

        unique_listings = self.remove_duplicates(all_listings)

        logging.info(
            "Category %s finished. Parsed %s listings, %s unique listings.",
            category_name,
            len(all_listings),
            len(unique_listings),
        )

        return unique_listings

    def scrape_all_pages(self):
        """Scrape every available result page for every configured category."""
        all_category_listings = []

        for category in AUCTION_CATEGORIES:
            category_listings = self.scrape_category_pages(category)
            all_category_listings.extend(category_listings)

        unique_listings = self.remove_duplicates(all_category_listings)

        logging.info(
            "All categories finished. Parsed %s category listings, %s unique listings.",
            len(all_category_listings),
            len(unique_listings),
        )

        return unique_listings

    def location_matches_target_district(self, location):
        """Return True when the location starts with one of the target districts."""
        clean_location = self.clean_text(location).lower()

        for district in TARGET_DISTRICTS:
            district_prefix = district.lower()

            # Correct match:
            # "Vilniaus r. sav. Mickūnų mstl. Gaidūnų g. 24"
            #
            # Incorrect match:
            # "Ignalinos r. sav. Dūkšto m. Vilniaus g. 61"
            if clean_location.startswith(district_prefix):
                return True

        return False

    def filter_by_district(self, listings):
        """Keep only listings whose location starts with a target district."""
        filtered = []

        for listing in listings:
            location = listing.get("location", "")

            if self.location_matches_target_district(location):
                filtered.append(listing)

        logging.info("Kept %s listings after district filtering", len(filtered))
        return filtered

    def remove_duplicates(self, listings):
        """Remove duplicate listings by listing_id or URL."""
        unique_listings = []
        seen_keys = set()

        for listing in listings:
            unique_key = listing.get("listing_id") or listing.get("url")

            if not unique_key or unique_key in seen_keys:
                continue

            seen_keys.add(unique_key)
            unique_listings.append(listing)

        return unique_listings

    def generate_test_data(self):
        """Generate sample data so CSV export can be tested without scraping."""
        logging.info("Generating fallback test data")

        now = datetime.now()

        return [
            {
                "listing_id": "test_001",
                "title": "Žemės sklypas 20 a.",
                "price": 14000.0,
                "expiration_date": (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M"),
                "location": "Molėtų r. sav. Videniškių k.",
                "url": "https://example.com/test_001",
                "auction_status": "Vykstančios",
                "category": "Land plots",
                "collected_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                "listing_id": "test_002",
                "title": "Namų valdos sklypas",
                "price": 22000.0,
                "expiration_date": (now + timedelta(days=15)).strftime("%Y-%m-%d %H:%M"),
                "location": "Vilniaus r. sav.",
                "url": "https://example.com/test_002",
                "auction_status": "Vykstančios",
                "category": "Buildings",
                "collected_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            },
        ]

    def save_to_csv(self, listings):
        """Save listings into today's CSV file inside the Data folder."""
        if not listings:
            logging.warning("No listings to save")
            return None

        today = datetime.now().strftime("%Y-%m-%d")
        csv_path = DATA_DIR / f"{today}_listings.csv"

        fieldnames = [
            "listing_id",
            "title",
            "price",
            "expiration_date",
            "location",
            "url",
            "auction_status",
            "category",
            "collected_at",
        ]

        try:
            with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listings)
        except PermissionError:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_path = DATA_DIR / f"{timestamp}_listings.csv"

            logging.warning(
                "Could not overwrite today's CSV. Saving to timestamped file: %s",
                csv_path,
            )

            with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(listings)

        logging.info("Saved %s listings to %s", len(listings), csv_path)
        return csv_path

    def save_debug_csv(self, listings):
        """Save parsed listings before filtering so district matching can be checked."""
        if not listings:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_path = DATA_DIR / f"{timestamp}_unfiltered_debug_listings.csv"

        fieldnames = [
            "listing_id",
            "title",
            "price",
            "expiration_date",
            "location",
            "url",
            "auction_status",
            "category",
            "collected_at",
        ]

        with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(listings)

        logging.info("Saved unfiltered debug CSV to %s", csv_path)
        return csv_path

    def print_statistics(self, listings):
        """Print and log a short summary of collected listings."""
        if not listings:
            print("No listings found.")
            return

        prices = [
            listing["price"]
            for listing in listings
            if isinstance(listing.get("price"), (int, float))
        ]

        print(f"Total listings saved: {len(listings)}")
        logging.info("Total listings saved: %s", len(listings))

        if prices:
            print(f"Average price: {sum(prices) / len(prices):.2f} EUR")
            print(f"Minimum price: {min(prices):.2f} EUR")
            print(f"Maximum price: {max(prices):.2f} EUR")

            logging.info("Average price: %.2f EUR", sum(prices) / len(prices))
            logging.info("Minimum price: %.2f EUR", min(prices))
            logging.info("Maximum price: %.2f EUR", max(prices))

    def run_collection(self):
        """Run the complete collection process."""
        logging.info("=== Listing collection started ===")

        try:
            parsed_listings = self.scrape_all_pages()

            if SAVE_UNFILTERED_DEBUG_CSV:
                debug_csv_path = self.save_debug_csv(parsed_listings)
                if debug_csv_path:
                    print(f"Debug CSV with all parsed listings: {debug_csv_path}")

            filtered_listings = self.filter_by_district(parsed_listings)
            final_listings = self.remove_duplicates(filtered_listings)

            if not final_listings and USE_TEST_DATA_WHEN_EMPTY:
                final_listings = self.generate_test_data()

            self.listings = final_listings
            csv_path = self.save_to_csv(final_listings)
            self.print_statistics(final_listings)

            if csv_path:
                print(f"CSV file created: {csv_path}")

            logging.info("=== Listing collection finished ===")

        except Exception as error:
            logging.exception("Critical error during listing collection")
            print(f"Collection failed: {error}")


def main():
    """Run one immediate collection."""
    collector = ListingCollector()
    collector.run_collection()


def schedule_job():
    """Run the collector every day at 08:00."""
    logging.info("Scheduler started. Collection will run every day at 08:00.")

    schedule.every().day.at("08:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_job()
    else:
        main()
