#!/usr/bin/env python3
"""
CQC Email Builder for CareOwl Campaign
Downloads CQC data and builds email target list

Usage:
    python cqc_email_builder.py download
    python cqc_email_builder.py process cqc_data.csv
    python cqc_email_builder.py build-list cqc_data.csv --max 500
"""

import re
import sys
import csv
import json
import time
import requests
from pathlib import Path
from urllib.parse import urlparse
from email_scraper import scrape_website_for_emails, guess_email_patterns

# CQC data portal URLs
CQC_LOCATIONS_URL = "https://api.cqc.org.uk/public/v1/locations"

# Headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def download_cqc_data(output_file='cqc_care_homes.csv', max_pages=None):
    """
    Download care home data from CQC API.
    Free, no API key required.
    """
    print("Downloading CQC care home data...")

    all_locations = []
    page = 1
    per_page = 500

    while True:
        if max_pages and page > max_pages:
            break

        url = f"{CQC_LOCATIONS_URL}?page={page}&perPage={per_page}&careHome=Y"

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            data = response.json()

            locations = data.get('locations', [])
            if not locations:
                break

            all_locations.extend(locations)
            print(f"  Page {page}: {len(locations)} locations (total: {len(all_locations)})")

            # Check if more pages
            total = data.get('total', 0)
            if len(all_locations) >= total:
                break

            page += 1
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break

    # Save to CSV
    if all_locations:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Get all possible fields
            fields = set()
            for loc in all_locations:
                fields.update(loc.keys())
            fields = sorted(list(fields))

            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_locations)

        print(f"\nSaved {len(all_locations)} care homes to {output_file}")

    return all_locations


def get_location_details(location_id):
    """Get detailed info for a specific location."""
    url = f"{CQC_LOCATIONS_URL}/{location_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json()
    except:
        return None


def process_cqc_csv(filepath, rating_filter=None):
    """
    Process CQC CSV and extract useful fields.
    Optionally filter by rating (Good, Requires improvement, etc.)
    """
    results = []

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Extract key fields (field names vary in different exports)
            name = row.get('name', row.get('Location Name', row.get('locationName', '')))

            # Try different field name variations
            rating = (row.get('currentRatings', {}) if isinstance(row.get('currentRatings'), dict)
                     else row.get('Latest Overall Rating', row.get('overallRating', '')))

            # Handle nested JSON in some exports
            if isinstance(rating, dict):
                rating = rating.get('overall', {}).get('rating', '')

            website = row.get('website', row.get('Web Address', ''))

            # Contact info
            phone = row.get('mainPhoneNumber', row.get('Phone', ''))

            # Address
            address = row.get('postalAddressLine1', row.get('Address Line 1', ''))
            town = row.get('postalAddressTownCity', row.get('Town', ''))
            postcode = row.get('postalCode', row.get('Postcode', ''))

            # Provider info
            provider = row.get('providerId', row.get('Provider ID', ''))
            provider_name = row.get('providerName', row.get('Provider Name', ''))

            # Filter by rating if specified
            if rating_filter and rating and rating.lower() != rating_filter.lower():
                continue

            results.append({
                'name': name,
                'rating': rating,
                'website': website,
                'phone': phone,
                'address': address,
                'town': town,
                'postcode': postcode,
                'provider_id': provider,
                'provider_name': provider_name,
                'location_id': row.get('locationId', row.get('Location ID', ''))
            })

    return results


def build_email_list(cqc_data, max_targets=500, scrape_websites=True):
    """
    Build email target list from CQC data.
    Tries website scraping first, then falls back to pattern guessing.
    """
    targets = []

    print(f"\nBuilding email list from {len(cqc_data)} care homes...")
    print(f"Target: {max_targets} emails\n")

    for i, home in enumerate(cqc_data):
        if len(targets) >= max_targets:
            break

        name = home.get('name', '')
        website = home.get('website', '')
        rating = home.get('rating', '')

        if not name:
            continue

        print(f"[{i+1}] {name[:50]}...", end=' ')

        emails_found = []
        source = 'none'

        # Try scraping website first
        if website and scrape_websites:
            try:
                scraped = scrape_website_for_emails(website)
                if scraped:
                    emails_found = scraped
                    source = 'scraped'
                    print(f"SCRAPED: {len(scraped)}", end=' ')
            except Exception as e:
                pass

        # Fall back to domain guessing
        if not emails_found and website:
            domain = website.lower()
            if domain.startswith('http'):
                domain = urlparse(domain).netloc
            if domain.startswith('www.'):
                domain = domain[4:]

            if domain:
                # Generate patterns for generic emails
                guessed = [
                    f'info@{domain}',
                    f'contact@{domain}',
                    f'enquiries@{domain}',
                    f'manager@{domain}',
                    f'admin@{domain}',
                    f'office@{domain}',
                ]
                emails_found = guessed[:2]  # Just take info@ and contact@
                source = 'guessed'
                print(f"GUESSED: {domain}", end=' ')

        if emails_found:
            for email in emails_found:
                targets.append({
                    'care_home': name,
                    'email': email,
                    'website': website,
                    'rating': rating,
                    'town': home.get('town', ''),
                    'phone': home.get('phone', ''),
                    'source': source
                })
            print("OK")
        else:
            print("SKIP")

        time.sleep(0.3)  # Rate limiting

    return targets


def save_targets(targets, output_file='careowl_targets.csv'):
    """Save targets to CSV for email campaign."""
    if not targets:
        print("No targets to save!")
        return

    # Remove duplicates by email
    seen = set()
    unique = []
    for t in targets:
        if t['email'] not in seen:
            seen.add(t['email'])
            unique.append(t)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['care_home', 'email', 'website', 'rating', 'town', 'phone', 'source'])
        writer.writeheader()
        writer.writerows(unique)

    print(f"\nSaved {len(unique)} unique targets to {output_file}")

    # Stats
    by_source = {}
    for t in unique:
        src = t['source']
        by_source[src] = by_source.get(src, 0) + 1

    print("\nBy source:")
    for src, count in by_source.items():
        print(f"  {src}: {count}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'download':
        # Download fresh CQC data
        max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None
        download_cqc_data(max_pages=max_pages)

    elif command == 'process':
        if len(sys.argv) < 3:
            print("Usage: python cqc_email_builder.py process <cqc_data.csv>")
            sys.exit(1)

        filepath = sys.argv[2]
        rating = sys.argv[3] if len(sys.argv) > 3 else None

        data = process_cqc_csv(filepath, rating_filter=rating)
        print(f"Processed {len(data)} entries")

        # Show sample
        for entry in data[:5]:
            print(f"  - {entry['name']}: {entry['website'] or 'no website'}")

    elif command == 'build-list':
        if len(sys.argv) < 3:
            print("Usage: python cqc_email_builder.py build-list <cqc_data.csv> [--max N]")
            sys.exit(1)

        filepath = sys.argv[2]
        max_targets = 500

        if '--max' in sys.argv:
            idx = sys.argv.index('--max')
            max_targets = int(sys.argv[idx + 1])

        # Process CSV
        data = process_cqc_csv(filepath)
        print(f"Loaded {len(data)} care homes from CSV")

        # Build email list
        targets = build_email_list(data, max_targets=max_targets)

        # Save
        save_targets(targets)

    elif command == 'quick-build':
        # Quick mode: download limited data and build list
        print("Quick build mode - downloading sample data...")
        download_cqc_data('cqc_sample.csv', max_pages=2)

        data = process_cqc_csv('cqc_sample.csv')
        targets = build_email_list(data, max_targets=100, scrape_websites=False)
        save_targets(targets, 'careowl_quick_targets.csv')

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
