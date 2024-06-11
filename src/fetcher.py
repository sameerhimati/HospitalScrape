import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
TIMEOUT = 10

def fetch_sitemap(url):
    headers = {'User-Agent': USER_AGENT}
    sitemap_url = f"{url}/sitemap.xml"
    try:
        response = requests.get(sitemap_url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'xml')
    except requests.RequestException as e:
        logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
        return None

def fetch_page(url):
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Error fetching page {url}: {e}")
        return None

def calculate_relevance(content, keywords):
    score = 0
    for keyword in keywords:
        occurrences = len(re.findall(keyword, content, re.IGNORECASE))
        score += occurrences
    return score

def fetch_and_process_pages(hospital_id, base_url, keywords):
    pages = []
    sitemap = fetch_sitemap(base_url)
    if sitemap:
        urls = [loc.text for loc in sitemap.find_all('loc')]
        for url in urls:
            page_content = fetch_page(url)
            if page_content:
                content = page_content.get_text()
                score = calculate_relevance(content, keywords)
                pages.append((url, content, score))
    
    pages.sort(key=lambda x: x[2], reverse=True)
    return pages[:3]
