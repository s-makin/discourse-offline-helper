import requests
import logging
import pathlib
import re
import csv
import sys

"""
Generic Discourse utility functions
"""

def get_raw_markdown(url: str) -> str:
    """
    Queries a URL and returns its raw markdown contents. If the response fails, returns an empty string.

    Parameters
    ----------
    url : str
        Full URL of the raw markdown content (e.g. 'https://discourse.charmhub.io/raw/9729').

    Returns
    -------
    str
        Raw markdown content if the request is successful, otherwise an empty string.
    """

    response = requests.get(url)
    if not response.ok:
        logging.debug(f"{url} not found")
        return ''

    return response.text

def parse_discourse_navigation_table(index_topic_markdown: str) -> list:
    """
    Extracts the navigation table from a raw Discourse topic.

    Parameters
    ----------
    index_topic_markdown : str
        Raw markdown content of the index topic.

    Returns
    -------
    list
        A list of dictionaries representing each row of the navigation table. 
        Each dictionary contains the 'Level', 'Path', and 'Navlink' keys, 
        e.g. [{'Level': '1', 'Path': 'slug-a', 'Navlink': '[Page A](/t/123)'}].
    """
    # Look for '[details=Navigation]'\n and \n'[/details]'
    match = re.search(
        r"\[details=Navigation]\n(.*?)\n\[\/details]",
        index_topic_markdown,
        flags=re.DOTALL,
    )
    if not match:
        logging.error("ERROR: No navigation table found in index topic. Exiting program.")
        sys.exit(1)
    
    # Extract content inside `[details]` markers (i.e. the navtable)
    table = match.group(1).strip()

    # Convert Markdown table to list[dict[str, str]] by parsing as CSV
    # (https://stackoverflow.com/a/78254495)
    rows: list[dict] = list(csv.DictReader(table.split("\n"), delimiter="|"))

    # Remove row after heading (e.g. "|---|---|---|")
    rows = rows[1:]

    navigation_table: list[dict[str, str]] = [
        {key.strip(): value.strip() for key, value in row.items() if key != ""}
        for row in rows
    ]
    
    return navigation_table

def download_topic(path: str, url : str = None) -> None:
    """
    Downloads a Discourse topic to a markdown file.

    Parameters
    ----------
    path : str
        Relative path to the file, e.g. '/docs/topic'.
    url : str, optional
        URL of the raw Discourse topic, e.g. 'https://discourse.charmhub.io/raw/9729'. 
        Default is None.
    """
    
    text = get_raw_markdown(url)

    output_path = pathlib.Path(path).with_suffix('.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    logging.info(f"Downloaded {output_path}.")