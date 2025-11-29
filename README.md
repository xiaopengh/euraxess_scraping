# EURAXESS Web Scraper

A Python-based web scraper for extracting research job opportunities from [EURAXESS](https://euraxess.ec.europa.eu), the pan-European platform for researcher mobility and career development.

## Authors
+ Pablo Román-Naranjo Varela
+ Adrián Vicente Gómez

## Author after fork
+ Xiaopeng Zhang

## Project Overview

This project was developed as part of the 'Tipología y ciclo de vida de los datos' course in the [Data Science MSc at UOC](https://estudios.uoc.edu/es/masters-universitarios/data-science/presentacion). The scraper automates the collection of research job postings from EURAXESS, enabling researchers to build custom datasets of opportunities in their field of interest.

**Key Features:**
- Search by keyword (e.g., "Data Science", "LLM", "Bioinformatics")
- Automatic pagination handling
- Extracts 30+ data fields per job posting
- Exports to CSV format for analysis
- Adaptive rate limiting to respect server resources

## Use Cases

While originally developed for data science job opportunities, this scraper can be used for any research field:
- Track emerging positions in specific domains (AI/ML, computational biology, climate science, etc.)
- Analyze geographic distribution of research opportunities
- Monitor funding patterns (EU-funded vs. national positions)
- Build datasets for career planning and trend analysis

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup

1. Install dependencies:
```bash
pip install -r scraping/requirements.txt
```

2. Use uv with virtual environments (recommended):
```bash
uv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
uv pip install -r scraping/requirements.txt
```
## Usage

### Basic Usage

1. Edit `scraping/main.py` to set your search keyword:
```python
keywords = "LLM"  # Change to your desired keyword
```

2. Run the scraper:
```bash
cd scraping
python main.py
```

3. The output CSV file will be created in the `scraping/` directory with the format `{keyword}.csv`

### Advanced Usage

You can also use the scraper programmatically:

```python
from utils import search_oportunities
import csv

# Search for opportunities
df_jobs = search_oportunities(keywords="Machine Learning")

# Export to CSV
df_jobs.to_csv("machine_learning_jobs.csv",
               quoting=csv.QUOTE_NONNUMERIC,
               sep=";",
               index=False)
```

## Extracted Data Fields

The scraper extracts comprehensive information for each job posting (30+ fields):

**Basic Information:**
- Title, Organization, Country, Posted Date

**Job Details:**
- Research Field, Researcher Profile, Contract Type
- Job Status, Hours per Week, Number of Positions
- Application Deadline, Offer Starting Date
- EU Funding Status, Reference Number

**Requirements:**
- Education Level, Languages, Language Level
- Years of Research Experience
- Skills/Qualifications, Specific Requirements

**Location:**
- Country, City, State/Province
- Postal Code, Street, Company/Institute

**Additional Information:**
- Offer Description, Benefits
- Application URL, Contact Email, Contact Website

## Example Output

Sample data from a "Data Science" keyword search (original dataset published on Zenodo: doi:[10.5281/zenodo.5636238](https://zenodo.org/record/5636238#.YYBLe57MJhG)):

| Title | Organization | Country | Research Field | Hours/Week | Application URL |
|-------|-------------|---------|----------------|------------|-----------------|
| Data Scientist | Centro de Biología Molecular Severo Ochoa | Spain | Biological sciences, Computer science | 37.5 | mailto:m.llorens@csic.es |
| Data scientist - Postdoctoral researcher | Radboud University Medical Center | Netherlands | Physics | 36.0 | [Link](https://www.academictransfer.com/...) |

## How It Works

![Application Schema](/images/schema.png "Application Schema")

The scraper follows this workflow:

1. **Search Query Construction**: Builds EURAXESS URL with keyword filter using the current URL format (as of Nov 2025):
   ```
   https://euraxess.ec.europa.eu/jobs/search?f%5B0%5D=keywords%3A"{keyword}"
   ```

2. **Pagination Handling**: Automatically detects the total number of result pages and iterates through all pages

3. **Job URL Collection**: Extracts individual job posting URLs from search result pages

4. **Data Extraction**: For each job posting, extracts detailed information using BeautifulSoup HTML parsing

5. **Rate Limiting**: Implements adaptive delays (2x response time) between requests to respect server resources

6. **Data Export**: Converts all extracted data to a pandas DataFrame and exports to CSV format

## Technical Architecture

**Core Components:**
- `scraping/main.py` - Entry point and configuration
- `scraping/utils.py` - Main scraping logic:
  - `search_oportunities(keywords)` - Orchestrates the scraping process
  - `_extract_job_data(job_soup)` - Parses individual job pages
  - `_scrape_jobs_to_dataframe(job_soups)` - Converts to DataFrame

**Dependencies:**
- BeautifulSoup4 - HTML parsing
- Pandas - Data manipulation
- Requests - HTTP requests
- Selenium - Web automation (available but currently unused)
- TQDM - Progress bars

## Important Notes

- **EURAXESS URL Format Update**: The scraper has been updated to work with the current EURAXESS URL structure (November 2025). If the website changes its structure, the HTML selectors in `utils.py` may need updates.

- **Rate Limiting**: The scraper includes built-in delays to avoid overwhelming the EURAXESS servers. Scraping large datasets will take time.

- **CSV Format**: Output files use semicolon (`;`) as delimiter and quote numeric values.

## Development

For interactive development and testing, a Jupyter notebook is available at `scraping/test.ipynb`.

## Citation

If you use this scraper or the datasets it generates, please cite the original work:

```
Román-Naranjo Varela, P., & Vicente Gómez, A. (2021).
EURAXESS Research Job Opportunities Dataset.
Zenodo. https://doi.org/10.5281/zenodo.5636238
```

## License

This project and all datasets derived from it are released under CC BY-NC-SA 4.0 License. [See more](https://github.com/avicenteg/euraxess_scraping/blob/master/LICENSE.md)
