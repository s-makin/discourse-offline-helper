import os
from slugify import slugify
from pathlib import Path
import logging
import re
from utils import *

class DiscourseItem:
    """
    A discourse navigation item represented by one row of the navtable.
    This class is meant to be managed exclusively by the :class:`DiscourseHandler`.

    :param navtable_row: e.g. {'Level': 1, 'Path': tutorial, 'Navlink': '[Tutorial](/t/123)}
    :type navtable_row: dict

    A DiscourseItem object contains properties that are calculated by this class automatically
    and properties that must be filled in externally.
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
    
    # Properties set by DiscourseHandler
    filepath = Path()
    isFolder = False
    isTopic = True

    def __init__(self, navtable_row: dict, configuration) -> None:

        self.config = configuration

        # Get values from Navigation table row
        if navtable_row['Level']:
            self.navtable_level = int(navtable_row['Level'])
        else:
            self.isValid = False # item is not valid if 'Level' column is empty
            return
        if self.navtable_level == 0:
            self.navtable_level = 1  # level 0 is the same hierarchy as 1. makes filepath calculation easier.

        self.navtable_path = navtable_row['Path']

        self.navtable_navlink = navtable_row['Navlink']
        if not self.navtable_navlink:
            self.isValid = False # item is not valid if 'Navlink' column is empty
            return

        # Get title, topic ID, and URL from the 'Navlink' column
        self.__parse_navtable_navlink()

        if self.topic_id == self.config['home_topic_id']:
            self.isHomeTopic = True

        # Set filename parameter
        self.__parse_filename()
    
    def update_filepath(self, path: Path):
        """
        Updates the file path of the item.

        :param path: New file path
        :type path: Path
        """
        self.filepath = path
        self.filename = path.stem
        if self.config['use_title_as_filename']:
            self.title = self.filename

    def __parse_filename(self):
        """
        Sets the filename based on the configuration.
        """
        if self.config['use_title_as_filename'] or self.navtable_path == '':
            self.filename = slugify(self.title)
        else:
            self.filename = slugify(self.navtable_path)

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
        self.url = f"https://{self.config['instance']}/raw/{self.topic_id}"
        
class DiscourseHandler:
    """
    This is a client-facing handler class with methods to manage one set of Discourse documentation.
    It contains methods to generate the directory structure of the documentation set and download.

    :param home_topic_id:Unique ID of the index/overview discourse topic containing the navtable without '/t/', e.g. '1234'.
    :type home_topic_id: str
    """

    def __init__(self, configuration: dict, index_topic_raw: str = '') -> None:
        self.config = configuration

        self._items = []
        self.__generate_items_list(index_topic_raw)

    def __generate_items_list(self, index_topic_raw: str = '') -> None:
        """
        Populates :param self._items: with :class:`DiscourseItem` objects generated from the navigation table.
        """
        if not index_topic_raw:
            if not self.config['home_topic_id'].isdigit():
                raise ValueError(f"Index topic ID '{self.config['home_topic_id']}' contains non-digit characters. Make sure to exclude '/t/'.")
            self._index_topic_url = f"https://{self.config['instance']}/raw/{self.config['home_topic_id']}"
            index_topic_raw = get_raw_markdown(self._index_topic_url)

            logging.info(f"\nParsing navigation table in index topic {self._index_topic_url}...")
            
        navtable_raw = parse_discourse_navigation_table(index_topic_raw)

        logging.info(f"\nGenerating discourse navigation items...")
        for row in navtable_raw:
            logging.debug(f"  {row}")
            item = DiscourseItem(row, self.config)
            if not item.isValid:
                logging.debug(f"Row {row} is not valid. Skipping.")
                continue
            self._items.append(item)

        # If index/home page was not in the navtable, add to items manually
        # TODO: expect Index as title or path
        index_topic = [x for x in self._items if x.topic_id == self.config['home_topic_id']]
        if not index_topic:
            index_navlink = f"[Index](/t/{self.config['home_topic_id']})"
            index_row = {'Level': '1', 'Path': 'index', 'Navlink': index_navlink}
            self._items.append(DiscourseItem(index_row, self.config))

    def calculate_item_type(self) -> None:
        """
        Calculates whether each item is a folder, topic, or both (i.e. a header with a landing page).
        Default values are: isFolder = False, isTopic = True

        For example, the navigation items below would be evaluated as follows:
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

                # Case 1: Current item is a folder if the next item is one level deeper
                if next_item_level == (current_item_level + 1):
                    self._items[i].isFolder = True
                # Case 2: Current item is a top-level folder with a landing page and no children
                elif current_item_level == 1 and next_item_level == 1 and self._items[i].url:
                    self._items[i].isFolder = True
            # Current item is a folder and NOT a topic if the URL is empty
            if not self._items[i].url:
                self._items[i].isFolder = True
                self._items[i].isTopic = False

    def calculate_filepaths(self) -> None:
            """
            Calculates the relative path of each item based on their level.

            For example, the navigation items below:
            | Level   | Path | Navlink |
            |---------|------|---------|
            | 1 | slug-a   | [Category A](/t/123) |
            | 2 | slug-a1  | [Page A1]() |
            | 3 | slug-a11 | [Subpage A11](/t/124) |

            are assigned the paths:
            /category-a
            /category-a/page-a1
            /category-a/page-a1/subpage-a11
            """
            stack = []
            for i in range(len(self._items)):
                while len(stack) >= int(self._items[i].navtable_level):
                    stack.pop()

                stack.append(self._items[i].filename)
                filepath_string = '/'.join(stack)

                path = Path(filepath_string)

                # If a topic is also a folder, append filename such that topic.md gets downloaded into /topic/topic.md
                if self._items[i].isTopic and self._items[i].isFolder:
                    self._items[i].filepath = self.config['docs_directory'] / path / path.name
                else:
                    self._items[i].filepath = self.config['docs_directory'] / path

    def download(self) -> None:
        """
        Downloads all topics from their URLs into the paths calculated by :meth:`calculate_filepaths`.
        """
        logging.debug("")
        for item in self._items:
            if item.isTopic:
                logging.debug(
                    f"\nDownloading '{item.title}' to '{item.filepath}' from URL '{item.url}'...")
                
                item.filepath.parent.mkdir(parents=True, exist_ok=True) # make sure parent folders exist
                if item.filepath.exists(): # if file already exists, remove
                    os.remove(item.filepath)
                
                download_topic(path=item.filepath, url=item.url)