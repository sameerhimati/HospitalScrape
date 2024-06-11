import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
TIMEOUT = 10
ENCODINGS = ['utf-8', 'iso-8859-1', 'windows-1252']

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
        return parse_content_with_encodings(response)
    except requests.RequestException as e:
        logger.error(f"Error fetching page {url}: {e}")
        return None

def parse_content_with_encodings(response):
    for encoding in ENCODINGS:
        try:
            response.encoding = encoding
            content = response.text
            return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            logger.warning(f"Error parsing content with encoding {encoding}: {e}")
    logger.error("Failed to parse content with all tried encodings.")
    return None

def calculate_relevance(content, keywords):
    documents = [content] + keywords
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:])
    relevance_score = cosine_similarities.mean()
    return relevance_score

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
