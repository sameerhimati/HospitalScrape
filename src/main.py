import logging
import requests
from src.fetcher import fetch_sitemap, fetch_page
from src.parser import extract_sitemap_urls, extract_search_results, extract_wait_times
from src.crawler import crawl_site
from src.searcher import search_site
from src.database import init_db, save_web_page, update_last_fetched, get_unprocessed_urls

logging.basicConfig(filename='logs/scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def main():
    init_db()  # Initialize the database and create tables if they don't exist
    logger.info("Database initialized")

    # Fetch URLs from the database
    urls = get_unprocessed_urls()

    # Define the keywords to use for crawling
    keywords = ['ER wait times', 'emergency room wait', 'wait time']

    # Process each hospital URL
    for hospital_id, hospital_url in urls:
        logger.info(f"Scraping data for hospital: {hospital_url}")
        try:
            # Try sitemap first
            sitemap_soup = fetch_sitemap(hospital_url)
            sitemap_urls = extract_sitemap_urls(sitemap_soup) if sitemap_soup else []

            # Try site search
            search_query = 'ER wait times'
            search_soup = search_site(hospital_url, search_query)
            search_results = extract_search_results(search_soup) if search_soup else []

            # Try crawling
            found_urls = crawl_site(hospital_url, keywords)

            # Combine all found URLs
            all_found_urls = set(sitemap_urls + search_results + found_urls)

            # Fetch and store web pages with relevance scores
            for url in all_found_urls:
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    content = response.content
                    wait_time = extract_wait_times(content)
                    relevance_score = 1.0 if wait_time else 0.0  # Simple relevance scoring example
                    save_web_page(hospital_id, url, content, relevance_score)
                except requests.RequestException as e:
                    logger.error(f"Failed to fetch URL {url}: {e}")

            # Update the last_fetched timestamp for the hospital URL
            update_last_fetched(hospital_id)

            logger.info("Scraping completed. Found URLs:")
            for url in all_found_urls:
                logger.info(url)
        except Exception as e:
            logger.error(f"An error occurred while scraping data for hospital {hospital_url}: {e}")

if __name__ == '__main__':
    main()
