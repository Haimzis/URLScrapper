import argparse
import concurrent.futures
import itertools
import os
import queue
from dataclasses import dataclass
from typing import Optional, List, Union
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import multiprocessing

from config import CANDIDATES_LABELS, MODEL_NAME, MODEL_TYPE, RESULTS_TABLE, SCRAPER_RESULTS_DB, MAX_LENGTH
from sql_operations import SqlOperations

from utils import extract_text, extract_metadata, extract_title, extract_links, \
    remove_duplicate_words, remove_special_characters, load_restoration_checkpoint, save_restoration_checkpoint

PKL_RESTORATION_FILE = 'last_crush_checkpoint.pkl'

failed_queue = queue.Queue(maxsize=100)


@dataclass
class StateNode:
    url: str
    source_url: Optional[str]
    depth: int


def scrape_url(current_state: StateNode, sql_ops: SqlOperations) -> List[StateNode]:
    """
    Scrapes the given URL, extracts page features, classifies the topic of the page, and inserts the results into
    the database. Returns the next states nodes(URLs, their source, depth).

    :param current_state: The current state of the web scraper.
    :param sql_ops: A SqlOperations instance to perform database operations.
    :return: A list of StateNode objects representing the next state of the web scraper.
    """
    try:
        # Download the HTML content of the page
        response = requests.get(current_state.url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page features
        links = extract_links(soup)
        title = extract_title(soup)
        meta_description, meta_keywords = extract_metadata(soup)
        text = extract_text(soup)

        # Combine features into a single string
        feature_string = ' '.join([title, text, meta_description, meta_keywords])
        feature_string = remove_special_characters(remove_duplicate_words(feature_string.lower()))

        # Classify the topic of the page
        # I'm using CPU -> using pipeline in batches is discouraged by hugging face.
        # Otherwise, I'd use a different process that will process results in batches.
        predicted_topic = classify_topic(feature_string)

        # Insert the results into the database
        # In general, using transactions in batches it's better.
        sql_ops.insert_row(RESULTS_TABLE, [
            current_state.url,
            current_state.source_url,
            current_state.depth,
            title,
            str(links),
            predicted_topic
        ])

        # Return the next states nodes
        return [StateNode(link, current_state.url, current_state.depth + 1) for link in links]

    except Exception as e:
        # Handle any errors that occur during scraping
        print(f"Error scraping {current_state.url}: {e}")
        failed_queue.put(current_state)
        return []


def classify_topic(feature_string: str) -> str:
    """
    Classifies the topic of a given text using a pre-trained transformer model.

    :param feature_string: The input text to classify.
    :return: The predicted topic.
    """
    topic_classifier = pipeline(MODEL_TYPE, model=MODEL_NAME, tokenizer=MODEL_NAME, candidate_labels=CANDIDATES_LABELS)
    logics = topic_classifier(feature_string, truncation=True, max_length=MAX_LENGTH)
    predicted_topic = logics['labels'][0]
    return predicted_topic


def scrape_recursive(initial_state: Union[StateNode, List[StateNode]], max_depth: int, sql_ops: SqlOperations, visited_urls=None) -> None:
    """
    Recursively scrapes URLs up to a certain depth and stores the results in a database.

    :param initial_state: The initial state of the web scraper.
    :param max_depth: The maximum depth (stop condition).
    :param sql_ops: A SqlOperations instance to perform database operations.
    """
    states = [initial_state] if isinstance(initial_state, StateNode) else initial_state
    visited_urls = set() if visited_urls is None else visited_urls

    while len(states) > 0:
        # Use multithreading to scrape URLs concurrently for faster results
        with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() - 1) as executor:
            returned_states = executor.map(lambda state: scrape_url(state, sql_ops), states)
            next_url_nodes = list(itertools.chain.from_iterable(returned_states))

        states = [node for node in next_url_nodes if node.url not in visited_urls and node.depth < max_depth]

        if not failed_queue.empty():
            save_restoration_checkpoint(states, visited_urls)
            raise RuntimeError


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="initial URL")
    parser.add_argument("--max-depth", help="maximum depth", type=int)
    args = parser.parse_args()

    # Initialize the database connection and create the table
    sql_ops = SqlOperations(SCRAPER_RESULTS_DB)
    sql_ops.create_table(RESULTS_TABLE, [
        'url TEXT',
        'source_url TEXT',
        'depth INTEGER',
        'title TEXT',
        'links TEXT',
        'topic TEXT'
    ])

    initial_state = StateNode(url=args.url, source_url=None, depth=0)
    visited_urls = None

    if os.path.exists(PKL_RESTORATION_FILE):
        initial_state, visited_urls = load_restoration_checkpoint()

    # scrape recursively
    scrape_recursive(initial_state, args.max_depth, sql_ops, visited_urls)


if __name__ == '__main__':
    main()
