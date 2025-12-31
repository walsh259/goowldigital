#!/usr/bin/env python3
"""
Email Scraper Toolkit for Go Owl Digital
Free methods for finding business emails

Usage:
    python email_scraper.py scrape-website https://example-carehome.co.uk
    python email_scraper.py scrape-list websites.txt
    python email_scraper.py guess-emails "John Smith" example-carehome.co.uk
    python email_scraper.py verify email@example.com
"""

import re
import sys
import csv
import json
import time
import socket
import smtplib
import requests
from urllib.parse import urlparse, urljoin
from pathlib import Path

# Disable SSL warnings for scraping
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Common email patterns
EMAIL_PATTERNS = [
    '{first}@{domain}',
    '{first}.{last}@{domain}',
    '{first}{last}@{domain}',
    '{f}{last}@{domain}',
    '{f}.{last}@{domain}',
    '{first}_{last}@{domain}',
    '{last}@{domain}',
    'info@{domain}',
    'contact@{domain}',
    'enquiries@{domain}',
    'admin@{domain}',
    'manager@{domain}',
    'office@{domain}',
]


def extract_emails_from_text(text):
    """Extract all email addresses from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    # Filter out common false positives
    filtered = []
    for email in emails:
        email = email.lower()
        # Skip image files, CSS, JS
        if any(ext in email for ext in ['.png', '.jpg', '.gif', '.css', '.js']):
            continue
        # Skip example emails
        if 'example.com' in email or 'example.org' in email:
            continue
        filtered.append(email)
    return list(set(filtered))


def scrape_website_for_emails(url, follow_links=True):
    """
    Scrape a website for email addresses.
    Checks main page, contact page, about page.
    """
    emails = set()
    visited = set()

    # Normalize URL
    if not url.startswith('http'):
        url = 'https://' + url

    parsed = urlparse(url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"

    # Pages to check
    pages_to_check = [
        url,
        urljoin(base_domain, '/contact'),
        urljoin(base_domain, '/contact-us'),
        urljoin(base_domain, '/about'),
        urljoin(base_domain, '/about-us'),
        urljoin(base_domain, '/team'),
        urljoin(base_domain, '/staff'),
    ]

    for page_url in pages_to_check:
        if page_url in visited:
            continue
        visited.add(page_url)

        try:
            response = requests.get(page_url, headers=HEADERS, timeout=10, verify=False)
            if response.status_code == 200:
                found = extract_emails_from_text(response.text)
                emails.update(found)

                # Also check for mailto: links
                mailto_pattern = r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                mailto_emails = re.findall(mailto_pattern, response.text)
                emails.update([e.lower() for e in mailto_emails])

        except Exception as e:
            pass  # Silently skip failed pages

        time.sleep(0.5)  # Be nice to servers

    return list(emails)


def guess_email_patterns(full_name, domain):
    """
    Generate possible email addresses based on name and domain.
    """
    # Clean the name
    parts = full_name.strip().lower().split()
    if len(parts) < 2:
        # Just first name
        first = parts[0] if parts else 'info'
        last = ''
        f = first[0] if first else ''
    else:
        first = parts[0]
        last = parts[-1]  # Use last part as surname
        f = first[0]

    # Clean domain
    domain = domain.lower().strip()
    if domain.startswith('http'):
        domain = urlparse(domain).netloc
    if domain.startswith('www.'):
        domain = domain[4:]

    guesses = []
    for pattern in EMAIL_PATTERNS:
        try:
            email = pattern.format(
                first=first,
                last=last,
                f=f,
                domain=domain
            )
            if email and '@' in email and not email.startswith('@'):
                guesses.append(email)
        except:
            pass

    return guesses


def verify_email_smtp(email, timeout=10):
    """
    Verify if an email address exists using SMTP.
    Note: Many servers block this, so results may be unreliable.
    """
    try:
        domain = email.split('@')[1]

        # Get MX record
        import dns.resolver
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(mx_records[0].exchange)

        # Connect to mail server
        server = smtplib.SMTP(timeout=timeout)
        server.connect(mx_host)
        server.helo('gmail.com')
        server.mail('test@gmail.com')
        code, message = server.rcpt(email)
        server.quit()

        return code == 250
    except:
        return None  # Unable to verify


def verify_email_simple(email):
    """
    Simple email verification - just check if domain has MX records.
    More reliable than SMTP check.
    """
    try:
        domain = email.split('@')[1]
        socket.gethostbyname(domain)
        return True
    except:
        return False


def process_cqc_csv(filepath):
    """
    Process CQC data CSV and extract domains for email scraping.
    """
    results = []

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract relevant fields (CQC CSV structure)
            location_name = row.get('Location Name', row.get('Name', ''))
            manager = row.get('Registered Manager', row.get('Manager', ''))
            website = row.get('Website', row.get('Web Address', ''))
            rating = row.get('Latest Overall Rating', row.get('Rating', ''))

            if website:
                results.append({
                    'name': location_name,
                    'manager': manager,
                    'website': website,
                    'rating': rating
                })

    return results


def scrape_google_for_email(company_name, location='UK'):
    """
    Search Google for company email (uses HTML scraping, may hit rate limits).
    """
    query = f'{company_name} {location} email contact'
    search_url = f'https://www.google.com/search?q={requests.utils.quote(query)}'

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            emails = extract_emails_from_text(response.text)
            return emails
    except:
        pass

    return []


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'scrape-website':
        if len(sys.argv) < 3:
            print("Usage: python email_scraper.py scrape-website <url>")
            sys.exit(1)

        url = sys.argv[2]
        print(f"Scraping {url}...")
        emails = scrape_website_for_emails(url)

        if emails:
            print(f"\nFound {len(emails)} email(s):")
            for email in emails:
                print(f"  {email}")
        else:
            print("No emails found on website.")

    elif command == 'scrape-list':
        if len(sys.argv) < 3:
            print("Usage: python email_scraper.py scrape-list <file.txt>")
            sys.exit(1)

        filepath = sys.argv[2]
        output_file = 'scraped_emails.csv'

        with open(filepath, 'r') as f:
            websites = [line.strip() for line in f if line.strip()]

        print(f"Scraping {len(websites)} websites...")

        results = []
        for i, url in enumerate(websites, 1):
            print(f"[{i}/{len(websites)}] {url}")
            emails = scrape_website_for_emails(url)
            for email in emails:
                results.append({'website': url, 'email': email})
            time.sleep(1)  # Rate limiting

        # Save results
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['website', 'email'])
            writer.writeheader()
            writer.writerows(results)

        print(f"\nSaved {len(results)} emails to {output_file}")

    elif command == 'guess-emails':
        if len(sys.argv) < 4:
            print("Usage: python email_scraper.py guess-emails \"Full Name\" domain.com")
            sys.exit(1)

        name = sys.argv[2]
        domain = sys.argv[3]

        print(f"Generating email patterns for {name} at {domain}:\n")
        guesses = guess_email_patterns(name, domain)
        for email in guesses:
            print(f"  {email}")

    elif command == 'verify':
        if len(sys.argv) < 3:
            print("Usage: python email_scraper.py verify <email>")
            sys.exit(1)

        email = sys.argv[2]
        print(f"Verifying {email}...")

        # Simple domain check
        if verify_email_simple(email):
            print(f"  Domain exists: YES")
        else:
            print(f"  Domain exists: NO")
            sys.exit(1)

        # Try SMTP verification (may not work)
        print("  SMTP verification: Attempting...")
        result = verify_email_smtp(email)
        if result is True:
            print(f"  SMTP verification: VALID")
        elif result is False:
            print(f"  SMTP verification: INVALID")
        else:
            print(f"  SMTP verification: UNABLE TO VERIFY (server blocked)")

    elif command == 'process-cqc':
        if len(sys.argv) < 3:
            print("Usage: python email_scraper.py process-cqc <cqc_data.csv>")
            sys.exit(1)

        filepath = sys.argv[2]
        print(f"Processing CQC data from {filepath}...")

        data = process_cqc_csv(filepath)
        print(f"Found {len(data)} entries with websites")

        # Save websites for scraping
        with open('cqc_websites.txt', 'w') as f:
            for entry in data:
                if entry['website']:
                    f.write(entry['website'] + '\n')

        # Save full data
        with open('cqc_processed.json', 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved website list to cqc_websites.txt")
        print(f"Saved full data to cqc_processed.json")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
