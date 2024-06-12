from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_sitemap_urls(soup):
    urls = [loc.get_text() for loc in soup.find_all('loc')]
    logger.info(f"Extracted sitemap URLs: {urls}")
    return urls

def extract_search_results(soup):
    results = [a['href'] for a in soup.find_all('a', href=True)]
    logger.info(f"Extracted search results: {results}")
    return results

def extract_wait_times(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    wait_time_keywords = ['wait time', 'waiting time', 'ER wait time', 'emergency room wait time']
    
    for keyword in wait_time_keywords:
        for tag in soup.find_all(text=lambda text: text and keyword in text.lower()):
            if tag.parent:
                text = tag.parent.get_text(separator=' ', strip=True)
                numbers = [int(s) for s in text.split() if s.isdigit()]
                if numbers:
                    wait_time = f"{numbers[0]} minutes"
                    logger.info(f"Extracted wait time: {wait_time}")
                    return wait_time
    
    logger.info("No wait time found")
    return None
