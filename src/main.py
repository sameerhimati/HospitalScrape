import logging
import requests
from src.fetcher import fetch_sitemap, fetch_and_process_pages
from src.parser import extract_sitemap_urls, extract_search_results, extract_wait_times
from src.database import init_db, drop_tables, save_web_page, update_last_fetched, get_unprocessed_urls, save_wait_time
from src.crawler import crawl_site
from src.searcher import search_site

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
            # Try site search
            search_query = 'ER wait times'
            logger.info(f"Searching site with query: {search_query}")
            search_soup = search_site(hospital_url, search_query)
            search_results = extract_search_results(search_soup) if search_soup else []
            logger.info(f"Search results: {search_results}")

            search_results = [url for url in search_results if url.startswith('https://')]

            # If search is successful, fetch and process pages for the search results
            if search_results:
                logger.info(f"Found search results. Fetching and processing pages.")
                pages = fetch_and_process_pages(hospital_id, search_results, keywords)
                for page in pages:
                    save_web_page(page['hospital_id'], page['url'], page['content'])
                    wait_times = extract_wait_times(page['content'])
                    for wait_time in wait_times:
                        save_wait_time(page['hospital_id'], wait_time)
            else:
                # If search fails, try crawling
                logger.info(f"Search failed. Crawling the site.")
                found_urls = crawl_site(hospital_url, keywords)
                pages = fetch_and_process_pages(hospital_id, found_urls, keywords)
                for page in pages:
                    save_web_page(page['hospital_id'], page['url'], page['content'])
                    wait_times = extract_wait_times(page['content'])
                    for wait_time in wait_times:
                        save_wait_time(page['hospital_id'], wait_time)

            # Update the last fetched timestamp for the hospital URL
            update_last_fetched(hospital_id)
            logger.info(f"Updated last fetched timestamp for hospital ID: {hospital_id}")

            logger.info("Scraping completed. Processed URLs:")
            for page in pages:
                logger.info(page['url'])
        except Exception as e:
            logger.error(f"An error occurred while scraping data for hospital {hospital_url}: {e}")

if __name__ == "__main__":
    main()
