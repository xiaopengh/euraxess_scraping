# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EURAXESS Web Scraper - A Python web scraper for extracting research job opportunities from the EURAXESS platform (https://euraxess.ec.europa.eu). Built as part of the UOC Data Science MSc program for generating datasets of research job postings.

## Setup and Dependencies

```bash
# Install dependencies (Python 3.11+)
pip install -r scraping/requirements.txt

# Activate virtual environment (if using .venv)
source .venv/bin/activate
```

## Running the Scraper

```bash
# From project root
cd scraping
python main.py
```

The scraper will:
1. Search EURAXESS for jobs matching the keyword (default: "LLM" in main.py)
2. Scrape all pages of results
3. Extract detailed job information from each listing
4. Export to CSV file named `{keyword}.csv`

## Architecture

### Core Components

**scraping/main.py**
- Entry point for the scraper
- Configures search keyword
- Calls `search_oportunities()` and exports to CSV with semicolon delimiter

**scraping/utils.py**
- `search_oportunities(keywords)`: Main scraper function that:
  1. Builds EURAXESS search URL with keyword filter format: `?f%5B0%5D=keywords%3A"{keyword}"`
  2. Determines total pages by parsing pagination (`ecl-pagination__item--last`)
  3. Iterates through all result pages collecting job URLs
  4. Fetches each job page with proportional delays (2x response time)
  5. Returns pandas DataFrame with all extracted data

- `_extract_job_data(job_soup)`: Extracts 30+ fields from individual job pages including:
  - Basic info: title, organization, country, dates
  - Job details: contract type, hours/week, positions, researcher profile
  - Requirements: education, languages, experience, skills
  - Location: city, state, postal code, street
  - Contact: email, website, application URL
  - Descriptions: offer description, benefits, specific requirements

- `_scrape_jobs_to_dataframe(job_soups)`: Converts list of BeautifulSoup objects to DataFrame

### EURAXESS HTML Structure (as of Nov 2025)

The scraper targets these specific HTML elements:
- Search results count: `<h2 id="search_results_count"><span>(N)</span></h2>`
- Pagination: `<li class="ecl-pagination__item ecl-pagination__item--last">`
- Job titles: `<h3 class="ecl-content-block__title">` with href pattern `/jobs/\d+`
- Job page title: `<h1 class="ecl-content-block__title">`
- Organization links: `<a href="/partnering/organisations/profile/...">`
- Country: `<span class="ecl-label--highlight">`
- Job details: `<dt class="ecl-description-list__term">` / `<dd>` pairs
- Sections: `<div class="ecl-u-type-bold">` headers with following `<div class="ecl">` content

### Development Notes

**Testing and Development**
- `scraping/test.ipynb`: Jupyter notebook for interactive development/testing of scraping logic
- Contains prototypes of functions later moved to utils.py

**Rate Limiting**
- Implements adaptive delays: `sleep(2 * response_delay)` after each job page request
- Uses polite headers including User-Agent and DNT

**Error Handling**
- Returns None for missing fields rather than raising exceptions
- Uses optional chaining with conditional checks for all extractions

## Data Output

CSV files are exported with:
- Semicolon (`;`) as delimiter
- Numeric fields quoted (`csv.QUOTE_NONNUMERIC`)
- Filename format: `{keyword}.csv`

## Important Context

- This is an academic project (MSc thesis work) with focus on data science job opportunities
- The original dataset was published on Zenodo: doi:10.5281/zenodo.5636238
- Licensed under CC BY-NC-SA 4.0
- EURAXESS URL structure was updated in Nov 2025 - the scraper uses the current format
