# Go Owl Digital - Email Outreach Scripts

Free methods for building email lists and prospecting.

## Scripts

### 1. email_scraper.py
Basic email extraction toolkit.

```bash
# Scrape a website for emails
python email_scraper.py scrape-website https://example-carehome.co.uk

# Scrape multiple websites from file
python email_scraper.py scrape-list websites.txt

# Generate email patterns from name
python email_scraper.py guess-emails "John Smith" example.co.uk

# Verify email domain exists
python email_scraper.py verify email@example.com

# Process CQC CSV export
python email_scraper.py process-cqc cqc_data.csv
```

### 2. cqc_email_builder.py
Automated CareOwl target list builder using free CQC data.

```bash
# Download CQC care home data (free API, no key needed)
python cqc_email_builder.py download

# Process existing CQC CSV
python cqc_email_builder.py process cqc_data.csv

# Build email list (scrapes websites + guesses emails)
python cqc_email_builder.py build-list cqc_data.csv --max 500

# Quick test (downloads sample, no scraping)
python cqc_email_builder.py quick-build
```

Output: `careowl_targets.csv` with columns:
- care_home, email, website, rating, town, phone, source

### 3. companies_house.py
UK business data lookup (requires free API key).

```bash
# Get free API key: https://developer.company-information.service.gov.uk/

# Set API key
export COMPANIES_HOUSE_API_KEY="your_key_here"

# Search companies
python companies_house.py search "Luxury Wood Company"

# Search by SIC code (road freight)
python companies_house.py search-sic 49410 --limit 100

# Get company details
python companies_house.py get-company 12345678

# Get directors
python companies_house.py get-officers 12345678
```

SIC codes for targeting:
- 49410: Road freight transport (Route Forge)
- 52290: Transportation support (DispatchOwl)
- 87100: Residential nursing care (CareOwl)
- 87300: Care for elderly/disabled (CareOwl)

## Workflow

### CareOwl Campaign (Priority)
```bash
# 1. Download CQC data
python cqc_email_builder.py download

# 2. Build target list (500 emails)
python cqc_email_builder.py build-list cqc_care_homes.csv --max 500

# 3. Output: careowl_targets.csv ready for email campaign
```

### DispatchOwl / Route Forge Campaign
```bash
# 1. Get Companies House API key (free)
# 2. Search by relevant SIC codes
python companies_house.py search-sic 49410 --limit 200

# 3. Output: sic_49410_targets.csv with company data
# 4. Use email_scraper.py to find emails from company websites
```

## Dependencies

```bash
pip install requests dnspython
```

## Rate Limiting
- All scripts include built-in delays
- CQC API: 0.5s between requests
- Website scraping: 0.5s between pages
- Companies House: 0.3s between requests

## GDPR Notes
- B2B cold email is legal in UK under PECR
- Must include opt-out in every email
- Must identify sender clearly
- Keep records of consent/opt-out
