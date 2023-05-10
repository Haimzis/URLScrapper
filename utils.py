import pickle
import re
from typing import List, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from main import PKL_RESTORATION_FILE, failed_queue


def extract_text(soup: BeautifulSoup) -> str:
    """
    Extracts text from the BeautifulSoup object and removes extra whitespaces.

    :param soup: A BeautifulSoup object.
    :return: A string containing the extracted text.
    """
    text = soup.get_text()
    return re.sub(r'\s+', ' ', text)


def remove_special_characters(text: str) -> str:
    """
    Removes special characters from a string using regex.

    :param text: The string to remove special characters from.
    :return: The cleaned string.
    """
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    return cleaned_text


def remove_duplicate_words(sentence: str) -> str:
    """
    Removes duplicate words from a sentence.

    :param sentence: The sentence to remove duplicate words from.
    :return: The sentence with duplicate words removed.
    """
    words = sentence.split()
    unique_words = list(set(words))
    filtered_sentence = " ".join(unique_words)
    return filtered_sentence


def extract_domain_name(url: str) -> str:
    """
    Extracts the domain name from a URL.

    :param url: The URL to extract the domain name from.
    :return: The extracted domain name.
    """
    parsed_url = urlparse(url)
    domain_name = parsed_url.netloc.split('.')
    if len(domain_name) > 2:
        domain_name = '.'.join(domain_name[-2:])
    else:
        domain_name = '.'.join(domain_name)
    return domain_name


def extract_metadata(soup: BeautifulSoup) -> tuple[str, str]:
    """
    Extracts the meta description and keywords from a BeautifulSoup object.

    :param soup: A BeautifulSoup object.
    :return: A tuple containing the extracted meta description and keywords.
    """
    meta_tags = soup.find_all('meta')
    meta_description = ''
    meta_keywords = ''
    for tag in meta_tags:
        if tag.get('name') == 'description':
            meta_description = tag.get('content')
        elif tag.get('name') == 'keywords':
            meta_keywords = tag.get('content')
    return meta_description, meta_keywords


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extracts the title from a BeautifulSoup object.

    :param soup: A BeautifulSoup object.
    :return: The extracted title.
    """
    return soup.title.string if soup.title and soup.title.string is not None else ""


def extract_links(soup: BeautifulSoup) -> List[str]:
    """
    Extracts all the links from a BeautifulSoup object.

    :param soup: A BeautifulSoup object.
    :return: A list of links.
    """
    return [link.get('href') for link in soup.find_all('a') if is_valid_link(link.get('href'))]


def is_valid_link(link: str) -> bool:
    """
    Checks if a link is valid.

    :param link: The link to check.
    :return: True if the link is valid, False otherwise.
    """
    parsed_url = urlparse(link)
    return bool(parsed_url.netloc)


def load_restoration_checkpoint() -> Tuple[List, set]:
    """
    Loads the restoration checkpoint from the pickle file.

    :return: A tuple containing the initial state and visited URLs.
    """
    with open(PKL_RESTORATION_FILE, 'rb') as f:
        # Load the contents of the file
        initial_state, visited_urls = pickle.load(f)
    return initial_state, visited_urls


def save_restoration_checkpoint(states: List, visited_urls: set) -> None:
    """
    Saves the current state of the web scraper to a pickle file for restoration.

    :param states: A list of StateNode objects representing the current state of the web scraper.
    :param visited_urls: A set of visited URLs.
    """
    failed_scrapes = list(failed_queue.queue)
    states_checkpoint = states + failed_scrapes
    with open(PKL_RESTORATION_FILE, 'wb') as f:
        pickle.dump((states_checkpoint, visited_urls), f)