import os
import json
import re
import requests
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm  # For the progress bar
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='scrape.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Constants for Boston.com
site_name = "Boston.com"
base_url = 'https://www.boston.com'
scrape_url = 'https://www.boston.com/category/real-estate/?p1=header_mainnav'

# JSON file to store scraped articles
json_file = "articles.json"

# Load previously scraped articles if available
if os.path.exists(json_file):
    with open(json_file, 'r') as f:
        scraped_articles = json.load(f)
    logging.info("[%s] Loaded existing articles from %s.", site_name, json_file)
else:
    scraped_articles = []
    logging.info("[%s] No existing articles file found; starting fresh.", site_name)

# Create a set of already-scraped URLs for quick lookup
scraped_urls = {article['url'] for article in scraped_articles}

logging.info("[%s] Starting scraping process for %s", site_name, scrape_url)
response = requests.get(scrape_url)
if response.status_code == 200:
    logging.info("[%s] Homepage fetched successfully.", site_name)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Define regex patterns for filtering links
    real_estate_pattern = re.compile(r"real-estate")
    date_pattern = re.compile(r"/\d{4}/\d{2}/\d{2}")
    
    # Extract all candidate article links
    href_list = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if real_estate_pattern.search(href) and date_pattern.search(href):
            href_list.append(href)
    logging.info("[%s] Found %d candidate article links.", site_name, len(href_list))
    
    # Remove duplicates and build full URLs
    href_list = list(set(href_list))
    full_links = []
    for href in href_list:
        if href.startswith("http"):
            full_links.append(href)
        else:
            full_links.append(base_url + href)
    logging.info("[%s] After processing, %d full links remain.", site_name, len(full_links))
    
    new_articles = []
    
    # Process each article with a progress bar
    for article_link in tqdm(full_links, desc="Scraping Boston.com Articles"):
        if article_link in scraped_urls:
            logging.info("[%s] Already scraped: %s", site_name, article_link)
            continue

        logging.info("[%s] Fetching article: %s", site_name, article_link)
        article_response = requests.get(article_link)
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Extract headline from <h1>
            hed_tag = article_soup.find('h1')
            hed = hed_tag.text.strip() if hed_tag else ""
            
            # Extract subhead from <h2> (if available)
            subhead_tag = article_soup.find('h2')
            subhead = subhead_tag.text.strip() if subhead_tag else ""
            
            # Extract article content by joining all <p> tags
            content = "\n".join(p.get_text(strip=True) for p in article_soup.find_all('p'))
            
            # Extract publication date from the URL (e.g., /2025/03/14/)
            date_match = re.search(r"/(\d{4})/(\d{2})/(\d{2})", article_link)
            if date_match:
                year, month, day = date_match.groups()
                raw_pub_date = f"{year}-{month}-{day}"
                try:
                    pub_date_obj = datetime(int(year), int(month), int(day))
                    pub_date = pub_date_obj.isoformat()
                except Exception as e:
                    logging.error("[%s] Error parsing date for %s: %s", site_name, article_link, e)
                    pub_date = ""
            else:
                raw_pub_date = ""
                pub_date = ""
            
            # Build the article data dictionary
            article_data = {
                "url": article_link,
                "raw_pub_date": raw_pub_date,
                "pub_date": pub_date,
                "hed": hed,
                "subhead": subhead,
                "content": content,
                "Outlet": site_name
            }
            
            new_articles.append(article_data)
            logging.info("[%s] Scraped article successfully: %s", site_name, article_link)
        else:
            logging.error("[%s] Failed to retrieve article: %s (status code: %s)",
                          site_name, article_link, article_response.status_code)
    
    # Save new articles if any were found
    if new_articles:
        scraped_articles.extend(new_articles)
        with open(json_file, 'w') as f:
            json.dump(scraped_articles, f, indent=4)
        logging.info("[%s] Saved %d new articles to %s.", site_name, len(new_articles), json_file)
    else:
        logging.info("[%s] No new articles were found.", site_name)
else:
    logging.error("[%s] Failed to retrieve main page. Status code: %s", site_name, response.status_code)
