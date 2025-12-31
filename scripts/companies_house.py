#!/usr/bin/env python3
"""
Companies House API - Free business data lookup
Requires free API key from: https://developer.company-information.service.gov.uk/

Usage:
    python companies_house.py search "Luxury Wood Company"
    python companies_house.py search-sic 49410 --limit 100  # Road freight
    python companies_house.py search-sic 87100 --limit 100  # Care homes
    python companies_house.py get-company 12345678
    python companies_house.py get-officers 12345678
"""

import os
import sys
import csv
import json
import base64
import requests
from time import sleep

# Get API key from environment
API_KEY = os.environ.get('COMPANIES_HOUSE_API_KEY', '')

# SIC codes for targeting
SIC_CODES = {
    '49410': 'Freight transport by road',
    '52290': 'Other transportation support activities',
    '87100': 'Residential nursing care activities',
    '87300': 'Residential care activities for elderly/disabled',
    '86210': 'General medical practice activities',
    '86220': 'Specialist medical practice activities',
    '47990': 'Other retail sale via mail order/internet',
}

BASE_URL = 'https://api.company-information.service.gov.uk'


def get_auth_header():
    """Generate auth header from API key."""
    if not API_KEY:
        print("Warning: No COMPANIES_HOUSE_API_KEY set")
        print("Get free key at: https://developer.company-information.service.gov.uk/")
        return {}

    # API key is used as username with empty password
    encoded = base64.b64encode(f'{API_KEY}:'.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}


def search_companies(query, items_per_page=50):
    """Search for companies by name."""
    url = f'{BASE_URL}/search/companies'
    params = {
        'q': query,
        'items_per_page': items_per_page
    }

    try:
        response = requests.get(url, headers=get_auth_header(), params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def search_by_sic(sic_code, limit=100):
    """
    Search for companies by SIC code.
    Note: CH API doesn't have direct SIC search, so we search for the SIC description.
    For proper SIC filtering, download bulk data from Companies House.
    """
    # This is a workaround - proper solution is bulk data download
    sic_desc = SIC_CODES.get(sic_code, sic_code)
    print(f"Searching for SIC {sic_code}: {sic_desc}")
    print("Note: API doesn't support direct SIC search. Consider bulk data download.")

    results = search_companies(sic_desc, items_per_page=limit)
    return results


def get_company(company_number):
    """Get full company details."""
    url = f'{BASE_URL}/company/{company_number}'

    try:
        response = requests.get(url, headers=get_auth_header(), timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None


def get_officers(company_number):
    """Get company officers (directors, etc.)."""
    url = f'{BASE_URL}/company/{company_number}/officers'

    try:
        response = requests.get(url, headers=get_auth_header(), timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None


def get_registered_office(company_number):
    """Get registered office address."""
    company = get_company(company_number)
    if company:
        return company.get('registered_office_address', {})
    return None


def build_target_list(companies, output_file='ch_targets.csv'):
    """Build CSV target list from company search results."""
    targets = []

    items = companies.get('items', [])
    print(f"\nProcessing {len(items)} companies...")

    for company in items:
        company_number = company.get('company_number', '')
        name = company.get('title', '')
        status = company.get('company_status', '')

        # Skip dissolved companies
        if status == 'dissolved':
            continue

        print(f"  {name}...", end=' ')

        # Get more details
        details = get_company(company_number)
        officers = get_officers(company_number)

        if details:
            address = details.get('registered_office_address', {})
            sic = details.get('sic_codes', [])

            # Get director names for email guessing
            director_names = []
            if officers:
                for officer in officers.get('items', []):
                    role = officer.get('officer_role', '')
                    if 'director' in role.lower():
                        director_names.append(officer.get('name', ''))

            targets.append({
                'company_name': name,
                'company_number': company_number,
                'status': status,
                'address': address.get('address_line_1', ''),
                'town': address.get('locality', ''),
                'postcode': address.get('postal_code', ''),
                'sic_codes': ', '.join(sic) if sic else '',
                'directors': ', '.join(director_names[:3]),  # First 3 directors
            })
            print("OK")
        else:
            print("SKIP")

        sleep(0.3)  # Rate limiting

    # Save to CSV
    if targets:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=targets[0].keys())
            writer.writeheader()
            writer.writerows(targets)

        print(f"\nSaved {len(targets)} companies to {output_file}")

    return targets


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nKnown SIC codes:")
        for code, desc in SIC_CODES.items():
            print(f"  {code}: {desc}")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'search':
        if len(sys.argv) < 3:
            print("Usage: python companies_house.py search <query>")
            sys.exit(1)

        query = sys.argv[2]
        print(f"Searching for: {query}")

        results = search_companies(query)
        if results:
            items = results.get('items', [])
            print(f"\nFound {len(items)} results:\n")
            for item in items[:10]:
                print(f"  {item.get('company_number')}: {item.get('title')}")
                print(f"    Status: {item.get('company_status')}")
                print(f"    Address: {item.get('address_snippet', 'N/A')}")
                print()

    elif command == 'search-sic':
        if len(sys.argv) < 3:
            print("Usage: python companies_house.py search-sic <sic_code> [--limit N]")
            sys.exit(1)

        sic_code = sys.argv[2]
        limit = 50

        if '--limit' in sys.argv:
            idx = sys.argv.index('--limit')
            limit = int(sys.argv[idx + 1])

        results = search_by_sic(sic_code, limit=limit)
        if results:
            build_target_list(results, f'sic_{sic_code}_targets.csv')

    elif command == 'get-company':
        if len(sys.argv) < 3:
            print("Usage: python companies_house.py get-company <company_number>")
            sys.exit(1)

        company_number = sys.argv[2]
        company = get_company(company_number)

        if company:
            print(json.dumps(company, indent=2))
        else:
            print("Company not found")

    elif command == 'get-officers':
        if len(sys.argv) < 3:
            print("Usage: python companies_house.py get-officers <company_number>")
            sys.exit(1)

        company_number = sys.argv[2]
        officers = get_officers(company_number)

        if officers:
            print(f"\nOfficers for company {company_number}:\n")
            for officer in officers.get('items', []):
                name = officer.get('name', '')
                role = officer.get('officer_role', '')
                appointed = officer.get('appointed_on', '')
                print(f"  {name}")
                print(f"    Role: {role}")
                print(f"    Appointed: {appointed}")
                print()
        else:
            print("Officers not found")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
