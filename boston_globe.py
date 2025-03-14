import os
import json
import re
import requests
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm  # Import tqdm for progress bar
from datetime import datetime  # Import datetime for date conversion

# Set up logging to a file named 'scrape.log'
logging.basicConfig(
    filename='scrape.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Constants for the Boston Globe
site_name = "Boston Globe"
base_url = 'https://www.bostonglobe.com'
scrape_url = f'{base_url}/business/real-estate/'

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

    # Regular expression pattern to match /YYYY/MM/DD followed by any characters
    pattern = re.compile(r"^/\d{4}/\d{2}/\d{2}.*")
    
    # Extract all <a> tags with href attributes that match the pattern
    article_links = [
        a['href'] for a in soup.find_all('a', href=True)
        if pattern.match(a['href'])
    ]
    logging.info("[%s] Found %d candidate article links.", site_name, len(article_links))
    
    # Remove duplicates and build full URLs
    full_links = ['https://www.bostonglobe.com' + link for link in set(article_links)]
    logging.info("[%s] After deduplication, %d full links remain.", site_name, len(full_links))
    
    new_articles = []
    
    # Wrap the article processing loop with tqdm for a progress bar
    for article_link in tqdm(full_links, desc="Scraping Boston Globe Articles"):
        if article_link in scraped_urls:
            logging.info("[%s] Already scraped: %s", site_name, article_link)
            continue

        logging.info("[%s] Fetching article: %s", site_name, article_link)
        article_response = requests.get(article_link)
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Extract headline (hed) from <h1>
            hed_tag = article_soup.find('h1')
            hed = hed_tag.text.strip() if hed_tag else ""
            
            # Extract subhead from <h2> if available
            subhead_tag = article_soup.find('h2')
            subhead = subhead_tag.text.strip() if subhead_tag else ""
            
            # Extract article content (from element with id 'article-body')
            body_tag = article_soup.find(id='article-body')
            content = body_tag.text.strip() if body_tag else ""
            
            # Extract publication date from URL (/YYYY/MM/DD)
            date_match = re.search(r"/(\d{4})/(\d{2})/(\d{2})", article_link)
            if date_match:
                year, month, day = date_match.groups()
                # Store the raw date string in the format found in the URL
                raw_pub_date = f"{year}-{month}-{day}"
                try:
                    pub_date_obj = datetime(int(year), int(month), int(day))
                    # Store as an ISO formatted string (e.g., "2025-03-14T00:00:00")
                    pub_date = pub_date_obj.isoformat()
                except Exception as e:
                    logging.error("[%s] Error parsing date for %s: %s", site_name, article_link, e)
                    pub_date = ""
            else:
                raw_pub_date = ""
                pub_date = ""
            
            article_data = {
                "url": article_link,
                "raw_pub_date": raw_pub_date,
                "pub_date": pub_date,
                "hed": hed,
                "subhead": subhead,
                "content": content,
                "Outlet": "Boston Globe"
            }
            
            new_articles.append(article_data)
            logging.info("[%s] Scraped article successfully: %s", site_name, article_link)
        else:
            logging.error("[%s] Failed to retrieve article: %s (status code: %s)", site_name, article_link, article_response.status_code)
    
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
