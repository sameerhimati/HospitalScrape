import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
TIMEOUT = 10

def search_site(url, query):
    search_urls = [
        f"{url}/search/?q={query}",
        f"{url}/search-results/?keyword={query.replace(' ', '+')}"
    ]
    headers = {'User-Agent': USER_AGENT}
    for search_url in search_urls:
        try:
            response = requests.get(search_url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            logger.info(f"Successfully fetched search results from {search_url}")
            return BeautifulSoup(response.content, 'html.parser')
        except requests.Timeout:
            logger.warning(f"Timeout when searching {search_url}. Moving to the next URL.")
        except requests.RequestException as e:
            logger.error(f"Error searching {search_url}: {e}")
    return None
