import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import snapshot_download
from .config import huggingface_token

from huggingface_hub import login
login(token=huggingface_token)

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
TIMEOUT = 10
ENCODINGS = ['utf-8', 'iso-8859-1', 'windows-1252']

# Initialize the Codestral-22B tokenizer and model
codestral_tokenizer = AutoTokenizer.from_pretrained("mistralai/Codestral-22B-v0.1")
codestral_model = AutoModelForCausalLM.from_pretrained("mistralai/Codestral-22B-v0.1")

# Initialize the Mistral-7B tokenizer and model
mistral_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
mistral_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")

prompt = """
**Objective:** Find the wait time for a hospital from the provided HTML content.

**Context:**
We are building a web scraping and analysis tool to extract wait time information for hospitals from their web pages. Our system crawls hospital websites, 
extracts relevant information from HTML content, and analyzes it to determine the estimated wait time for patients. 
The HTML content may vary in structure and formatting across different hospital websites.

**Task:**
Given a sample HTML content from a hospital webpage, extract and interpret the relevant information to determine the estimated wait time for patients visiting the hospital.

**Input:**
{html_content}

**Output:**
- Estimated wait time: [wait time value]
- Confidence level: [confidence score]

**Instructions:**
1. **HTML Content:** Paste the HTML content from the hospital webpage into the input field.
2. **Analysis:** The system will analyze the provided HTML content to identify relevant information related to the wait time.
3. **Output:** Once the analysis is complete, the system will provide the estimated wait time for the hospital along with a confidence score indicating the reliability of the prediction.

**Additional Information:**
- The wait time may be mentioned in various formats within the HTML content, such as text, tables, or embedded widgets.
- The system should consider contextual clues, such as headings, labels, or surrounding text, to accurately interpret the wait time information.
- In cases where the wait time is not explicitly stated, the system should employ natural language processing techniques to infer the wait time based on related information, such as appointment schedules, emergency room statistics, or patient reviews.
- The provided keywords for crawling and analysis: {keywords}
- The confidence score indicates the level of certainty associated with the estimated wait time. Higher confidence scores denote more reliable predictions, while lower scores may indicate ambiguity or insufficient information.
- Continuous evaluation and refinement of the system are necessary to improve accuracy and adaptability across different hospital websites and variations in HTML content structure.

**Example Input:**
<HTML content goes here>

**Example Output:**
- Estimated wait time: 45 minutes
- Confidence level: 0.85
"""

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

def process_with_codestral(text, max_tokens):
    inputs = codestral_tokenizer(text, return_tensors="pt")
    outputs = codestral_model.generate(**inputs, max_new_tokens=max_tokens)
    decoded_output = codestral_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded_output

def process_with_mistral(text, max_tokens):
    inputs = mistral_tokenizer(text, return_tensors="pt")
    outputs = mistral_model.generate(**inputs, max_new_tokens=max_tokens)
    decoded_output = mistral_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded_output

def fetch_and_process_pages(hospital_id, base_url, keywords, max_tokens=4096):
    pages = []

    # Attempt to fetch sitemap
    sitemap = fetch_sitemap(base_url)
    if sitemap:
        urls = [loc.text for loc in sitemap.find_all('loc')]
        for url in urls:
            page_content = fetch_page(url)
            if page_content:
                content = page_content.get_text()
                formatted_prompt = prompt.format(html_content=content, keywords=keywords)
                processed_content_codestral = process_with_codestral(formatted_prompt, max_tokens=max_tokens)
                processed_content_mistral = process_with_mistral(formatted_prompt, max_tokens=max_tokens)
                pages.append({'hospital_id': hospital_id, 'url': url, 'content_codestral': processed_content_codestral, 'content_mistral': processed_content_mistral})
        return pages

    # If sitemap not found, fetch pages directly from the base URL
    else:
        page_content = fetch_page(base_url)
        if page_content:
            content = page_content.get_text()
            formatted_prompt = prompt.format(html_content=content, keywords=keywords)
            processed_content_codestral = process_with_codestral(formatted_prompt, max_tokens=max_tokens)
            processed_content_mistral = process_with_mistral(formatted_prompt, max_tokens=max_tokens)
            pages.append({'hospital_id': hospital_id, 'url': base_url, 'content_codestral': processed_content_codestral, 'content_mistral': processed_content_mistral})
            return pages

    return pages
