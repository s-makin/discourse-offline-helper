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
    Queries a URL and returns its raw markdown contents. If the response fails, returns empty string.

    :param url: Full URL of the raw markdown content. e.g. 'https://discourse.charmhub.io/raw/9729'
    :type url: str
    :return: Raw markdown content
    :rtype: str
    """

    response = requests.get(url)
    if not response.ok:
        logging.debug(f"{url} not found")
        return ''

    return response.text

def parse_discourse_navigation_table(index_topic_markdown: str) -> list:
    """
    Extract navigation table from a raw discourse topic.

    :param index_topic_markdown: Raw markdown content of the index topic
    :type index_topic_markdown: str
    :return: List of dictionaries representing each row of the navtable
    E.g. [{'Level': '1', 'Path': 'slug-a', 'Navlink': '[Page A](/t/123)'}, {'Level': '2', 'Path': 'slug-b', 'Navlink': '[Page B](/t/124)'}]
    :rtype: list
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
    Download a discourse topic to a markdown file. Must use either `url` or `raw_text`.

    :param path: Relative path to the file. E.g. '/docs/topic'
    :type path: str
    :param url: (Optional) URL of the raw discourse topic. E.g. 'https://discourse.charmhub.io/raw/9729'
    :type url: str, optional
    :rtype: None
    """
    
    text = get_raw_markdown(url)

    output_path = pathlib.Path(path).with_suffix('.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    logging.info(f"Downloaded {output_path}.")