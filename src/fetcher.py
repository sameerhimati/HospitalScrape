import logging
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from .config import huggingface_token, groq_token
import torch
from groq import Groq

import ollama

#model = ollama.load_model("llama-3.7b")

client = Groq(api_key=groq_token)

login(token=huggingface_token)

logger = logging.getLogger(__name__)

device = torch.device('mps')

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
TIMEOUT = 10
ENCODINGS = ['utf-8', 'iso-8859-1', 'windows-1252']

# Initialize the Mistral-7B tokenizer and model
#mistral_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
#mistral_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3").to(device)

prompt = """
**Objective:** Find the wait time for a hospital from the provided content.

**Context:**
We are building a web scraping and analysis tool to extract wait time information for hospitals from their web pages. Our system crawls hospital websites, 
extracts relevant information from HTML content, and analyzes it to determine the estimated wait time for patients. 
The HTML content may vary in structure and formatting across different hospital websites.

**Task:**
Given a sample HTML content text from a hospital webpage, extract and interpret the relevant information to determine the estimated wait time for patients visiting the hospital.

**Input:**
{html_content}

**Output:**
- Estimated wait time: [wait time value]
- Confidence level: [confidence score]

**Instructions:**
1. **HTML Content:** Paste the HTML content from the hospital webpage into the input field.
2. **Analysis:** The system will analyze the provided HTML content to identify relevant information related to the wait time.
3. **Output:** Once the analysis is complete, the system will provide the estimated wait time for the hospital along with a confidence score indicating the reliability of the prediction. 
If you don't find a result, output None for the wait time with a confidence score of -1.

**Additional Information:**
- The wait time may be mentioned in various formats within the HTML content, such as text, tables, or embedded widgets.
- The system should consider contextual clues, such as headings, labels, or surrounding text, to accurately interpret the wait time information.
- In cases where the wait time is not explicitly stated, the system should employ natural language processing techniques to infer the wait time based on related information, such as appointment schedules, emergency room statistics, or patient reviews.
- The provided keywords for crawling and analysis: {keywords}
- The confidence score indicates the level of certainty associated with the estimated wait time. Higher confidence scores denote more reliable predictions, while lower scores may indicate ambiguity or insufficient information.
- Continuous evaluation and refinement of the system are necessary to improve accuracy and adaptability across different hospital websites and variations in HTML content structure.

**Example Input:**
My name is Jeff

**Example Output:**
- Estimated wait time: None
- Confidence level: -1
"""

user_prompt = """
**Objective:** Extract the wait time information from the provided markdown content. Remember I dont want averages or historical but live data which is posted on their website.

**Context:**
We are building a web scraping and analysis tool to extract wait time information for hospitals from their web pages. Our system crawls hospital websites, extracts relevant information, and analyzes it to determine the estimated wait time for patients. The content is provided in markdown format, which is cleaned up from the original HTML.

**Task:**
Given a sample markdown content from a hospital webpage, extract and interpret the relevant information to determine the estimated wait time for patients visiting the hospital.

**Input:**
{markdown_content}
"""


system_prompt = """
**Output:**
- Estimated wait time: [wait time value]
- Confidence level: [confidence score]

**Instructions:**
1. **Markdown Content:** Analyze the provided markdown content to identify relevant information related to the wait time.
2. **Analysis:** The system will parse the markdown content to find specific mentions of wait time information.
3. **Output:** Provide the estimated wait time for the hospital along with a confidence score indicating the reliability of the prediction. If no wait time is found, output "None" for the wait time with a confidence score of -1.

**Additional Information:**
- The wait time may be mentioned in various formats within the markdown content, such as text, lists, tables, or embedded information.
- Consider contextual clues such as headings, labels, or surrounding text to accurately interpret the wait time information.
- If the wait time is not explicitly stated, use natural language processing techniques to infer it based on related information, such as appointment schedules, emergency room statistics, or patient reviews.
- The confidence score indicates the level of certainty associated with the estimated wait time. Higher confidence scores denote more reliable predictions, while lower scores may indicate ambiguity or insufficient information.
- Continuous evaluation and refinement of the system are necessary to improve accuracy and adaptability across different hospital websites and variations in content structure.
- Dont forget, Remember I dont want averages or historical but live data which is posted on their website.


"""


def fetch_sitemap(url):
    headers = {'User-Agent': USER_AGENT}
    sitemap_url = f"{url}/sitemap.xml"
    try:
        response = requests.get('https://r.jina.ai/' + sitemap_url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'xml')
    except requests.RequestException as e:
        logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
        return None

import re

def fetch_page(url):
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        cleaned_content = clean_html_content(response.text)
        
        # Check if the cleaned content is a string
        if isinstance(cleaned_content, str):
            return cleaned_content
        print(cleaned_content.type)
        soup = BeautifulSoup(cleaned_content, 'html.parser')
        return parse_content_with_encodings(soup.get_text())
        
    except requests.RequestException as e:
        logger.error(f"Error fetching page {url}: {e}")
        return None

def clean_html_content(html_content):
    # Remove extra whitespace characters like newlines and tags
    cleaned_content = re.sub(r'\s+', ' ', html_content)
    return cleaned_content

def fetch_page_jina(url):
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get('https://r.jina.ai/' + url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        cleaned_content = response
        
        # Check if the cleaned content is a string
        return cleaned_content
        #print(cleaned_content.type)
        soup = BeautifulSoup(cleaned_content, 'html.parser')
        return parse_content_with_encodings(soup.get_text())
        
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

def process_with_mistral(text, max_tokens):
    logger.info(f"Processing text with Mistral model: {text[:200]}...")  # Log a snippet of the text
    try:
        print("zero!")
        inputs = mistral_tokenizer(text, return_tensors="pt").to(device)
        print("uno!")
        outputs = mistral_model.generate(inputs).to(device)
        print("dos!")
        decoded_output = mistral_tokenizer.decode(outputs[0], skip_special_tokens=True).to(device)
        print("tres!")
        logger.info(f"Processed output: {decoded_output[:200]}...")  # Log a snippet of the output
        return decoded_output
    except Exception as e:
        logger.error(f"Error processing with Mistral: {e}")
        return None

def process_with_groq(text, max_tokens):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": text
                },
                {
                    "role": "system",
                    "content": system_prompt
                }
            ],
            temperature=0,
            max_tokens=8192,
            top_p=1,
            stream=False,
            stop=None,
        )

        return completion.choices[0].message.content

        processed_output = ""
        for chunk in completion:
            processed_output += chunk.choices[0].delta.content or ""

        return processed_output
    except Exception as e:
        logger.error(f"Error processing with Groq: {e}")
        return None

def fetch_and_process_pages(hospital_id, base_urls, keywords, max_tokens=8192):
    pages = []
    logger.info(f"Fetching and processing pages for hospital {hospital_id} from {base_urls}")
    
    # Convert base_urls to a list if it's a single URL
    if not isinstance(base_urls, list):
        base_urls = [base_urls]
    
    for base_url in base_urls:
        # Attempt to fetch sitemap
        logger.info(f"Fetching sitemap for {base_url}")
        # sitemap = fetch_sitemap(base_url)
        sitemap = False
        if sitemap:
            logger.info(f"Found sitemap for {base_url}")
            urls = [loc.text for loc in sitemap.find_all('loc')]
            for url in urls:
                page_content = fetch_page_jina(url)
                if page_content:
                    content = page_content
                    formatted_prompt = prompt.format(html_content=content, keywords=keywords)
                    #processed_content_mistral = process_with_mistral(formatted_prompt, max_tokens=max_tokens)
                    processed_content_mistral = process_with_groq(formatted_prompt, max_tokens=max_tokens)
                    pages.append({'hospital_id': hospital_id, 'url': url, 'content_mistral': processed_content_mistral})
        else:
            # If sitemap not found, fetch pages directly from the base URL
            page_content = fetch_page_jina(base_url)
            if page_content:
                content = page_content
                #formatted_prompt = prompt.format(html_content=content, keywords=keywords)
                formatted_prompt = user_prompt.format(markdown_content=content)
                logger.info(f"Fetched content: {formatted_prompt[:200]}...")  # Log a snippet of the content
                #processed_content_mistral = process_with_mistral(formatted_prompt, max_tokens=max_tokens)
                processed_content_mistral = process_with_groq(formatted_prompt, max_tokens=max_tokens)
                logger.info(f"Processed content for {base_url}: {processed_content_mistral}")  # Log a snippet of the output
                pages.append({'hospital_id': hospital_id, 'url': base_url, 'content_mistral': processed_content_mistral})
    return pages
