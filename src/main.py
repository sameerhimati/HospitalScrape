import logging
import requests
from src.fetcher import fetch_sitemap, fetch_page, calculate_relevance
from src.parser import extract_sitemap_urls, extract_search_results, extract_wait_times
from src.crawler import crawl_site
from src.searcher import search_site
from src.database import init_db, drop_tables, save_web_page, update_last_fetched, get_unprocessed_urls, save_wait_time

logging.basicConfig(filename='logs/scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def main():
    drop_tables()  # Drop existing tables
    init_db()  # Initialize the database and create tables
    logger.info("Database initialized")

    # Fetch URLs from the database
    hospital_urls = get_unprocessed_urls()

    # Define the keywords to use for crawling
    keywords = ['ER wait times', 'emergency room wait', 'wait time']

    # Process each hospital URL
    for hospital_id, hospital_url in hospital_urls:
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

            # Extract wait times and save results to database
            for url in all_found_urls:
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    content = response.content
                    wait_time = extract_wait_times(content)
                    relevance_score = calculate_relevance(content, keywords)  # Improved relevance scoring
                    save_web_page(hospital_id, url, content, relevance_score)
                    if wait_time:
                        save_wait_time(hospital_id, wait_time)
                except requests.RequestException as e:
                    logger.error(f"Failed to fetch URL {url}: {e}")

            # Update the last fetched timestamp for the hospital URL
            update_last_fetched(hospital_id)

            logger.info("Scraping completed. Found URLs:")
            for url in all_found_urls:
                logger.info(url)
        except Exception as e:
            logger.error(f"An error occurred while scraping data for hospital {hospital_url}: {e}")

if __name__ == '__main__':
    main()
