import logging
import re
from bs4 import BeautifulSoup
from .database import get_unprocessed_html, update_processed_status

logger = logging.getLogger(__name__)

def extract_wait_times(html_content):
    """
    Extracts potential wait times from the HTML content.

    Args:
        html_content (str): The raw HTML content of a page.

    Returns:
        list of dict: A list of dictionaries containing potential wait times and their corresponding contexts.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator=' ')
    
    print(text_content)
    wait_times = []
    for match in re.finditer(r'\b(\d+)\s*(minutes?|hours?)\b', text_content, re.IGNORECASE):
        context = text_content[max(0, match.start() - 30):match.end() + 30]
        wait_times.append({
            'wait_time': match.group(),
            'context': context
        })

    return wait_times

def process_html_content():
    """
    Processes unprocessed HTML content from the database and extracts potential wait times.
    """
    unprocessed_html = get_unprocessed_html()
    for item in unprocessed_html:
        wait_times = extract_wait_times(item['html_content'])
        if wait_times:
            # Store wait times in the database (this part depends on your schema and requirements)
            pass
        update_processed_status(item['id'], True)

if __name__ == '__main__':
    process_html_content()
