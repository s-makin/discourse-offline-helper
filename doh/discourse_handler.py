from slugify import slugify
from pathlib import Path
import logging
import re
import sys
import requests
import csv

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

def search_for_navtable(text: str) -> str:
    """
    Searches for a Discourse navigation table in a raw markdown string.

    Parameters
    ----------
    text : str
        Raw markdown content of a Discourse topic.

    Returns
    -------
    str
        The navigation table content if found, otherwise an empty string.
    """
 
    # Look for '[details=Navigation]'\n and \n'[/details]'
    match = re.search(
        r"\[details=Navigation]\n(.*?)\n\[\/details]",
        text,
        flags=re.DOTALL,
    )

    if not match:
        return ""
    
    # Return content inside markers (i.e. the navtable)
    return match.group(1).strip()

def parse_discourse_navigation_table(index_topic_markdown: str, search=True) -> list:
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
   
    # Search for markers surrounding the navigation table
    table = ""
    if search:
        table = search_for_navtable(index_topic_markdown)
        if not table:
            sys.exit("ERROR: Navigation table not found. Exiting program.")
    else:
        table = index_topic_markdown
        
    # Convert Markdown table to list[dict[str, str]] by parsing as CSV
    # (https://stackoverflow.com/a/78254495)
    rows: list[dict] = list(csv.DictReader(table.split("\n"), delimiter="|"))

    if not rows:
        sys.exit("ERROR: Navigation table is seemingly empty. Exiting program.")

    # Remove row after heading ("|---|---|---|")
    rows = rows[1:]

    navigation_table = []
    for row in rows:
        cleaned_row = {}
        for key, value in row.items():
            if key != "" and value:
                cleaned_row[key.strip()] = value.strip()
            elif not value:
                continue
            
        navigation_table.append(cleaned_row)
    
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

    output_path = Path(path).with_suffix('.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    logging.info(f"Downloaded {output_path}.")

class DiscourseItem:
    """
    A discourse navigation item represented by one row of the navtable.
    This class is meant to be managed exclusively by the DiscourseHandler.

    Parameters
    ----------
    navtable_row : dict
        A dictionary representing a row of the navtable, e.g. {'Level': 1, 'Path': 'tutorial', 'Navlink': '[Tutorial](/t/123)'}
    configuration : dict
        A dictionary containing settings from `config.yaml`.

    Attributes
    ----------
    navtable_level : int
        The level of the item in the navigation table.
    navtable_path : str
        The path (i.e., the Discourse URL slug) from the navigation table.
    navtable_navlink : str
        The navlink from the navigation table.
    isHomeTopic : bool
        Whether the item is the home topic.
    isValid : bool
        If False, the item will be ignored.
    title : str
    topic_id : str
    url : str
    filename : str

    Attributes set by DiscourseHandler
    ----------
    filepath : Path
    isFolder : bool
    isTopic : bool
    """

    navtable_level = 0
    navtable_path = ''
    navtable_navlink = ''

    isHomeTopic = False
    isValid = True

    title = ''
    topic_id = ''
    url = ''
    filename = ''
    
    filepath = Path()
    isFolder = False
    isTopic = True

    def __init__(self, navtable_row: dict, configuration) -> None:
        if not navtable_row:
            self.isValid = False
            return

        self.config = configuration

        # Get 'Level' from navigation table
        # For consistent filepath calculations across different Navtables, the default level of root items must be 1.
        if navtable_row['Level']:
            self.navtable_level = int(navtable_row['Level'])
        else:
            self.isValid = False # item is not valid if 'Level' column is empty
            return
        if self.navtable_level == 0:
            self.navtable_level = 1  # level 0 items are treated as level 1 items

        # Get 'Path' (i.e.the Discourse URL slug) from navigation table
        self.navtable_path = navtable_row['Path']

        # Get 'Navlink' from navigation table
        self.navtable_navlink = navtable_row['Navlink']
        if not self.navtable_navlink:
            self.isValid = False # item is not valid if 'Navlink' column is empty
            return

        # Parse title, topic ID, and URL from the 'Navlink' column
        self.__parse_navtable_navlink()

        if self.topic_id == self.config['home_topic_id']:
            self.isHomeTopic = True

        # Set filename parameter
        self.filename = slugify(self.title)
    
    def update_filepath(self, path: Path):
        """
        Updates the file path of the item.

        Parameters
        ----------
        path : Path
            New file path
        """
        self.filepath = path
        self.filename = path.stem
        self.title = self.filename

    def __parse_navtable_navlink(self):
        """
        Parses 'Navlink' item to obtain `_url` and `_title`.

        Expected format: [Title](discourse link), e.g. '[Tutorial](/t/123)'
        """            
        # Look for capture groups "title" and "link" in the format [<title>](<link>)
        # E.g. [Example page](/t/123) will return "Example page" and "/t/123"
        match = re.fullmatch(r"\[(.*?)]\((.*?)\)", self.navtable_navlink)
        if not match:
            self.title = self.navtable_navlink
            logging.debug(
                f"No valid link was found for this row. Setting title to {self.title}")
            return

        self.title = match.group(1)
        link = match.group(2)

        if link == '':
            return
        elif link.startswith("http") and self.config['instance'] not in link:
            logging.debug(
                f"This row has an external link. This item will be ignored.")
            self.isValid = False
            return

        # Extract topic ID number
        self.topic_id = link.split("/")[-1]
        if not self.topic_id.isdigit():
            logging.error(
                f"ERROR: Topic ID is not valid for item 'Level: {self.navtable_level}, Path: {self.navtable_path}, Navlink: {self.navtable_navlink}'."
                 "\nMake sure the format of the 'Navlink' is '[Title](/t/123)', '[Title](/t/slug/123)', or empty. Exiting program.")
            sys.exit(1)
        self.url = f"https://{self.config['instance']}/raw/{self.topic_id}"
        
class DiscourseHandler:
    """
    Manages one set of Discourse documentation.
    It contains methods to generate the directory structure of the documentation set and download.

    Parameters
    ----------
    configuration : dict
        A dictionary containing settings from `config.yaml`.
    index_topic_raw : str, optional
        Raw content of the index topic, by default ''.

    Attributes
    ----------
    config : dict
        A dictionary containing settings from `config.yaml`.
    _items : list
        List of DiscourseItem objects.
    """

    def __init__(self, configuration: dict, index_topic_raw: str = '') -> None:
        self.config = configuration

        self._items = []
        self.__generate_items_list(index_topic_raw)

    def __generate_items_list(self, index_topic_raw: str = '') -> None:
        """
        Populates `_items` with `DiscourseItem` objects generated from the navigation table.
        """
        if not index_topic_raw:
            if not self.config['home_topic_id'].isdigit():
                raise ValueError(f"Index topic ID '{self.config['home_topic_id']}' contains non-digit characters. Make sure to exclude '/t/'.")
            
            self._index_topic_url = f"https://{self.config['instance']}/raw/{self.config['home_topic_id']}"
            index_topic_raw = get_raw_markdown(self._index_topic_url)

            logging.info(f"\nParsing navigation table in index topic {self._index_topic_url}...")
            
            navtable_raw = parse_discourse_navigation_table(index_topic_raw)
        else:
            navtable_raw = parse_discourse_navigation_table(index_topic_raw, search=False)

        logging.info(f"\nGenerating discourse navigation items...")
        for row in navtable_raw:
            logging.debug(f"  {row}")
            item = DiscourseItem(row, self.config)
            if not item.isValid:
                logging.debug(f"Row {row} is not valid. Skipping.")
                continue
            self._items.append(item)

        # If index/home page was not in the navtable, add to items manually
        index_topic = [x for x in self._items if x.topic_id == self.config['home_topic_id']]
        if not index_topic:
            index_navlink = f"[Home](/t/{self.config['home_topic_id']})"
            index_row = {'Level': '1', 'Path': 'index', 'Navlink': index_navlink}
            self._items.append(DiscourseItem(index_row, self.config))

    def calculate_item_type(self) -> None:
        """
        Calculates whether each item is a folder, topic, or both (i.e., a header with a landing page).
        
        Each item in the navigation table is evaluated based on its properties. Default values are:
        - `isFolder = False`
        - `isTopic = True`
        
        Examples
        --------
        The navigation items below are evaluated as follows:

        | Level   | Path | Navlink |
        |---------|------|---------|
        | 1 | slug-a  | [Category A](/t/123)    --> isFolder = true, isTopic = true
        | 2 | slug-a1 | [Page A1]()             --> isFolder = true, isTopic = false
        | 3 | slug-a11 | [Subpage A11](/t/124)  --> isFolder = false, isTopic = true
        | 2 | ...
        """

        for i in range(0, len(self._items)):
            if not self._items[i].isHomeTopic and (i < len(self._items) - 1):
                current_item_level = int(self._items[i].navtable_level)
                next_item_level = int(self._items[i+1].navtable_level)
                # Current item is a folder if the next item is one level deeper
                if next_item_level == (current_item_level + 1):
                    self._items[i].isFolder = True
            # Current item is a folder and NOT a topic if the URL is empty
            if not self._items[i].url:
                self._items[i].isFolder = True
                self._items[i].isTopic = False

    def calculate_filepaths(self) -> None:
            """
            Calculates the relative path of each item based on their level.

            Examples
            --------
            The navigation items below:

            | Level   | Path | Navlink |
            |---------|------|---------|
            | 1 | tutorial   | [Tutorial](/t/123) |
            | 2 | first-time  | [Deploy for the first time]() |
            | 3 | set-up | [Set up your environment](/t/124) |

            are assigned the paths:
            - /tutorial
            - /tutorial/deploy-for-the-first-time
            - /tutorial/deploy-for-the-first-time/set-up-your-environment
            """
            stack = []
            for i in range(len(self._items)):
                while len(stack) >= int(self._items[i].navtable_level):
                    stack.pop()

                stack.append(self._items[i].filename)
                filepath_string = '/'.join(stack)

                path = Path(filepath_string)

                if self._items[i].isTopic:
                    self._items[i].filepath = self.config['docs_directory'] / path.with_suffix('.md')
                    if self._items[i].isFolder:
                        self._items[i].filepath = (self.config['docs_directory'] / path / path.name).with_suffix('.md')
                elif self._items[i].isFolder:
                    self._items[i].filepath = self.config['docs_directory'] / path

    def download(self) -> None:
        """
        Downloads all topics from their URLs into the paths returned by calculate_filepaths()
        """
        logging.debug("")
        for item in self._items:
            if item.isTopic:
                logging.debug(
                    f"\nDownloading '{item.title}' to '{item.filepath}' from URL '{item.url}'...")
                
                item.filepath.parent.mkdir(parents=True, exist_ok=True) # make sure parent folders exist
                download_topic(path=item.filepath, url=item.url)