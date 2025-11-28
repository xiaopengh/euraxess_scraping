from bs4 import BeautifulSoup as BS
import csv
import pandas as pd
import re
import requests
from selenium import webdriver
import selenium.common.exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep, time
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

def search_oportunities(keywords):
    print("Starting search for opportunities with keywords:", keywords)
    # Header definition
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Accept-Language': 'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7',
        'Referer': 'https://google.com',
        'DNT': '1'
    }
    # Main page
    main_str = "https://euraxess.ec.europa.eu"
    # Keywords (i.e. job field: data science, data analyst etc...)
    keywords = str(keywords)
    # Join keywords and main page: web to scrape
    # Currently (11/2025), EURAXESS uses this format to search by keywords
    search_str = '?f%5B0%5D=keywords%3A"' + keywords.replace(" ", "%20") + '"'
    subdomain_str = main_str + "/jobs/search" + search_str
    # Subdomain request
    subdomain_rq = requests.get(subdomain_str, headers=headers)
    subdomain_rq.close()
    # If web is available, it will return 200 (i.e. Ok for scraping)
    if subdomain_rq.status_code == 200:
        print("Web is available for scraping")
    else:
        print("Something is wrong. Status code:", subdomain_rq.status_code)
    # Extract useful info from subdomain (keyword) page
    soup_subdomain = BS(subdomain_rq.content, "html.parser")
    # Extract number of offers/pages for subdomain_page (keywords):
    # offers_subdomain = soup_subdomain.find_all("h2", {"class": "text-center"})
    offers_subdomain = soup_subdomain.find_all("h2", id = "search_results_count")
    if offers_subdomain:
        span = offers_subdomain[0].find("span")
    else:
        print("No offers found")
    # Number of offers
    offers_count = re.findall(r'[0-9]+', str(span))[0] if span else "0"
    # offers_count = re.findall(r'[0-9]+', str(offers_subdomain))[1]
    # Number of pages
    pager_subdomain = soup_subdomain.find_all("li", {"class": "ecl-pagination__item ecl-pagination__item--last"})
    # pager_subdomain = soup_subdomain.find_all("li", {"class": "pager-current"})

    if offers_count == '0':  # If = 0, a message indicating the issue is showed.
        print("There are no offers with these keywords. Please, type other keywords")
    else:
        if len(pager_subdomain) > 0:  # if pages > 0, the function iterates, scraping each page to obtain info.
            pages_count_subdomain = pager_subdomain[0].find("a")
            pages_count_subdomain = re.findall(r'[0-9]+', str(pages_count_subdomain))[0]
            # pages_count_subdomain = re.findall(r'[0-9]+', str(pager_subdomain))[1]  # Number of pages (iterate purpose)
            print('Number of offers using the keyword "{}":'.format(keywords), offers_count, "in {} pages".format(pages_count_subdomain))
            # for loop to obtain job offer titles & URLs
            raw_titles_sub = []
            raw_href_sub = []
            job_soups = []

            for i in tqdm(range(int(pages_count_subdomain))):
                subdomain_pages_str = subdomain_str + "&page={}".format(i)  # String of keyword webpage i
                subdomain_pages_rq = requests.get(subdomain_pages_str, headers=headers, timeout=120)  # Request of this page
                subdomain_pages_rq.close()
                soup_subdomain_pages = BS(subdomain_pages_rq.content, "html.parser")  # page BeautifulSoup
                titles_subdomain = soup_subdomain_pages.find_all("h3", {"class": "ecl-content-block__title"})  # Obtain html line of titles
                for title in titles_subdomain:
                    suffix_href = "".join(re.findall(r'/jobs/\d+',str(title)))
                    href = main_str + suffix_href
                    raw_href_sub.append(href)   # Get offer URLs
                    raw_titles_sub.append(title.get_text().replace("\n",""))  # Get offer titles
            for url in tqdm(raw_href_sub):
                t0 = time()
                job_rq = requests.get(url, headers=headers, timeout=120)
                job_rq.close()
                job_soup = BS(job_rq.content, "html.parser")
                job_soups.append(job_soup)

                # sleep time proportional to response delay
                response_delay = time()-t0
                sleep(2* (response_delay))

            # Convert job soups to DataFrame
            df_jobs = _scrape_jobs_to_dataframe(job_soups)
            print("Scraping completed. Number of jobs scraped:", len(df_jobs))
            return df_jobs


def _extract_job_data(job_soup):
    """
    Extract structured job information from EURAXESS job page soup
    
    Parameters:
    job_soup: BeautifulSoup object of the job page
    
    Returns:
    dict: Structured job data
    """
    
    job_data = {}
    
    # Helper function to safely extract text from description lists
    def _get_dl_value(term_text):
        """Extract value from description list given the term"""
        dl_items = job_soup.find_all('dt', class_='ecl-description-list__term')
        for dt in dl_items:
            if term_text.lower() in dt.get_text(strip=True).lower():
                dd = dt.find_next_sibling('dd')
                if dd:
                    return dd.get_text(strip=True)
        return None
    
    # Extract title
    title_elem = job_soup.find('h1', class_='ecl-content-block__title')
    job_data['title'] = title_elem.get_text(strip=True) if title_elem else None
    
    # Extract organization
    org_link = job_soup.find('a', href=re.compile(r'/partnering/organisations/profile/'))
    job_data['organization'] = org_link.get_text(strip=True) if org_link else None
    
    # Extract country from label
    country_label = job_soup.find('span', class_='ecl-label--highlight')
    job_data['country'] = country_label.get_text(strip=True) if country_label else None
    
    # Extract posted date
    posted_meta = job_soup.find('li', string=re.compile(r'Posted on:'))
    if posted_meta:
        job_data['posted_date'] = posted_meta.get_text(strip=True).replace('Posted on:', '').strip()
    else:
        job_data['posted_date'] = None
    
    # Extract main job information from description lists
    job_data['research_field'] = _get_dl_value('Research Field')
    job_data['researcher_profile'] = _get_dl_value('Researcher Profile')
    job_data['positions'] = _get_dl_value('Positions')
    job_data['application_deadline'] = _get_dl_value('Application Deadline')
    job_data['contract_type'] = _get_dl_value('Type of Contract')
    job_data['job_status'] = _get_dl_value('Job Status')
    job_data['hours_per_week'] = _get_dl_value('Hours Per Week')
    job_data['offer_starting_date'] = _get_dl_value('Offer Starting Date')
    job_data['eu_funded'] = _get_dl_value('Is the job funded through the EU Research Framework Programme?')
    job_data['reference_number'] = _get_dl_value('Reference Number')
    
    # Extract offer description
    offer_desc_section = job_soup.find('h2', id='offer-description')
    if offer_desc_section:
        desc_div = offer_desc_section.find_next('div', class_='ecl')
        job_data['offer_description'] = desc_div.get_text(strip=True) if desc_div else None
    else:
        job_data['offer_description'] = None
    
    # Extract application URL
    apply_link = job_soup.find('a', class_='job-apply-button')
    job_data['application_url'] = apply_link['href'] if apply_link and 'href' in apply_link.attrs else None
    
    # Extract requirements
    job_data['education_level'] = _get_dl_value('Education Level')
    job_data['languages'] = _get_dl_value('Languages')
    job_data['language_level'] = _get_dl_value('Level')
    job_data['years_experience'] = _get_dl_value('Years of Research Experience')
    
    # Extract skills/qualifications
    skills_section = job_soup.find('div', class_='ecl-u-type-bold', string=re.compile(r'Skills/Qualifications'))
    if skills_section:
        skills_div = skills_section.find_next('div', class_='ecl')
        job_data['skills_qualifications'] = skills_div.get_text(strip=True) if skills_div else None
    else:
        job_data['skills_qualifications'] = None
    
    # Extract specific requirements
    specific_req_section = job_soup.find('div', class_='ecl-u-type-bold', string=re.compile(r'Specific Requirements'))
    if specific_req_section:
        req_div = specific_req_section.find_next('div', class_='ecl')
        job_data['specific_requirements'] = req_div.get_text(strip=True) if req_div else None
    else:
        job_data['specific_requirements'] = None
    
    # Extract benefits
    benefits_section = job_soup.find('div', class_='ecl-u-type-bold', string=re.compile(r'Benefits'))
    if benefits_section:
        benefits_div = benefits_section.find_next('div', class_='ecl')
        job_data['benefits'] = benefits_div.get_text(strip=True) if benefits_div else None
    else:
        job_data['benefits'] = None
    
    # Extract work location details
    job_data['work_location_count'] = _get_dl_value('Number of offers available')
    job_data['work_company'] = _get_dl_value('Company/Institute')
    job_data['work_city'] = _get_dl_value('City')
    job_data['work_state'] = _get_dl_value('State/Province')
    job_data['work_postal_code'] = _get_dl_value('Postal Code')
    job_data['work_street'] = _get_dl_value('Street')
    
    # Extract contact information
    contact_email_dd = job_soup.find('dt', string=re.compile(r'E-Mail'))
    if contact_email_dd:
        email_dd = contact_email_dd.find_next_sibling('dd')
        job_data['contact_email'] = email_dd.get_text(strip=True) if email_dd else None
    else:
        job_data['contact_email'] = None
    
    contact_website = job_soup.find('dt', string=re.compile(r'^Website$'))
    if contact_website:
        website_dd = contact_website.find_next_sibling('dd')
        website_link = website_dd.find('a') if website_dd else None
        job_data['contact_website'] = website_link['href'] if website_link and 'href' in website_link.attrs else None
    else:
        job_data['contact_website'] = None
    
    return job_data


# Convert multiple job soups to a pandas DataFrame
def _scrape_jobs_to_dataframe(job_soups):
    """
    Convert multiple job soups to a pandas DataFrame
    
    Parameters:
    job_soups: list of BeautifulSoup objects
    
    Returns:
    pd.DataFrame: DataFrame with all job data
    """
    jobs_list = []
    
    for job_soup in job_soups:
        job_data = _extract_job_data(job_soup)
        jobs_list.append(job_data)
    
    df = pd.DataFrame(jobs_list)
    return df