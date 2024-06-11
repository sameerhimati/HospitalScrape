from urllib.parse import urljoin
import re
from .fetcher import fetch_page

# Crawl site function, recusivly finds links/urls within the site with the same base URL to explorez

def crawl_site(base_url, keywords, max_depth=2):
    """
    Crawls a website starting from the given base URL and searches for URLs that contain any of the given keywords.

    Parameters:
        base_url (str): The base URL to start crawling from.
        keywords (list): A list of keywords to search for in the website's URLs.
        max_depth (int, optional): The maximum depth to crawl the website. Defaults to 2.

    Returns:
        list: A list of URLs that contain any of the given keywords.

    This function uses a breadth-first search algorithm to crawl the website starting from the base URL. It keeps track of the visited URLs to avoid revisiting them. For each URL visited, it fetches the page using the `fetch_page` function and searches for any URLs that contain any of the given keywords. If a matching URL is found, it is added to the `result_urls` list. The function continues crawling the website until all URLs have been visited or the maximum depth has been reached. Finally, it returns the list of URLs that contain any of the given keywords.

    Note:
        This function assumes that the `fetch_page` function is defined in the `fetcher.py` module and returns a BeautifulSoup object representing the fetched web page.
    """
    visited = set()
    to_visit = [(base_url, 0)]
    result_urls = []

    while to_visit:
        print('crawling...results so far: ', str(len(result_urls)))
        url, depth = to_visit.pop(0)
        if depth > max_depth or url in visited:
            continue

        visited.add(url)
        soup = fetch_page(url)
        if not soup:
            continue

        if any(re.search(keyword, soup.text, re.IGNORECASE) for keyword in keywords):
            result_urls.append(url)

        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            if base_url in full_url and full_url not in visited:
                to_visit.append((full_url, depth + 1))

    return result_urls
