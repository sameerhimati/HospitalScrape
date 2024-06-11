from bs4 import BeautifulSoup

def extract_sitemap_urls(soup):
    return [loc.get_text() for loc in soup.find_all('loc')]

def extract_search_results(soup):
    return [a['href'] for a in soup.find_all('a', href=True)]

def extract_wait_times(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    wait_time_keywords = ['wait time', 'waiting time', 'ER wait time', 'emergency room wait time']
    
    for keyword in wait_time_keywords:
        for tag in soup.find_all(text=lambda text: text and keyword in text.lower()):
            if tag.parent:
                text = tag.parent.get_text(separator=' ', strip=True)
                numbers = [int(s) for s in text.split() if s.isdigit()]
                if numbers:
                    return f"{numbers[0]} minutes"
    
    return None
