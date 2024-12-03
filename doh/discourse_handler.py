import os
from slugify import slugify
from pathlib import Path
import logging
import re
from utils import *
from conf import *

class DiscourseItem:
    """
    A discourse navigation item represented by one row of the navtable.
    This class is meant to be managed exclusively by the :class:`DiscourseHandler`.

    :param navtable_row: e.g. {'Level': 1, 'Path': tutorial, 'Navlink': '[Tutorial](/t/123)}
    :type navtable_row: dict

    A DiscourseItem object contains properties that are calculated by this class automatically
    and properties that must be filled in externally.
    """

    isFolder = False
    isTopic = True
    isIndexTopic = False
    filepath = Path()

    def __init__(self, navtable_row: dict) -> None:
        self.isValid = True

        if navtable_row['Level']:
            self.navtable_level = int(navtable_row['Level'])
        else:
            self.isValid = False
        if self.navtable_level == 0:
            self.navtable_level = 1  # level 0 is the same hierarchy as 1. this makes filepath calculation easier.

        self.navtable_path = navtable_row['Path']
        self.navtable_navlink = navtable_row['Navlink']
        if not self.navtable_navlink:
            self.isValid = False

        # Set title and url parameters
        self.title = ''
        self.topic_id = ''
        self.url = ''
        self.__parse_navtable_navlink()

        if self.topic_id == conf['INDEX_TOPIC_ID']:
            self.isIndexTopic = True

        # Set filename parameter
        self.filepath = ''
        self.__parse_filename()
    
    def update_filepath(self, path: Path):
        self.filepath = path
        self.filename = path.stem
        if conf['USE_TITLE_AS_FILENAME']:
            self.title = self.filename

    def __parse_filename(self):
        if conf['USE_TITLE_AS_FILENAME'] or self.navtable_path == '':
            self.filename = slugify(self.title)
        else:
            self.filename = slugify(self.navtable_path)

    def __parse_navtable_navlink(self):
        """
        Parses 'Navlink' item to obtain `_url` and `_title`.

        Expected format: [Title](discourse link), e.g. '[Tutorial](/t/123)'
        """
        if not self.navtable_navlink:
            logging.debug(
                f"No valid Navlink was found for this row.")
            
        # Regex looks for capture groups "title" and "link" in the format [<title>](<link>),
        # where <title> and <link> can be any set of characters.
        match = re.fullmatch(r"\[(.*?)]\((.*?)\)", self.navtable_navlink)
        if not match:
            self.title = self.navtable_navlink
            logging.debug(
                f"No valid Navlink was found for this row. Setting title to {self.title}")
            return

        self.title = match.group(1)
        link = match.group(2)

        # If link is empty, navigation item is just a folder and not a topic.
        if link == '':
            return
        elif link.startswith("http") and conf['DISCOURSE_INSTANCE'] not in link:
            logging.debug(
                f"This row has an external link. This item will be ignored.")
            self.isValid = False
            return

        # Extract topic ID number
        self.topic_id = link.split("/")[-1]
        self.url = f"https://{conf['DISCOURSE_INSTANCE']}/raw/{self.topic_id}"
        
class DiscourseHandler:
    """
    This is a client-facing handler class with methods to manage one set of Discourse documentation.
    It contains methods to generate the directory structure of the documentation set and download.

    :param index_topic_id:Unique ID of the index/overview discourse topic containing the navtable without '/t/', e.g. '1234'.
    :type index_topic_id: str
    """

    def __init__(self):

        self._items = []
        self.__generate_items_list()

    def __generate_items_list(self) -> None:
        """
        Populates :param self._items: with :class:`DiscourseItem` objects generated from the navigation table.
        """
        self._index_topic_url = f"https://{conf['DISCOURSE_INSTANCE']}/raw/{conf['INDEX_TOPIC_ID']}"
        index_topic_raw = get_raw_markdown(self._index_topic_url)

        logging.debug(f"Parsing navigation table in index topic {self._index_topic_url}...")
        navtable_raw = parse_discourse_navigation_table(index_topic_raw)

        logging.debug(f"Generating discourse navigation items...")
        for row in navtable_raw:
            logging.debug(f"  {row}")
            item = DiscourseItem(row)
            if not item.isValid:
                logging.debug(f"Item is not valid. Skipping.")
                continue
            self._items.append(item)

        # If index/home page was not in the navtable, add to items manually
        # TODO: expect Index as title or path
        index_topic = [x for x in self._items if x.topic_id == conf['INDEX_TOPIC_ID']]
        if not index_topic:
            index_navlink = f"[Index](/t/{conf['INDEX_TOPIC_ID']})"
            index_row = {'Level': '1', 'Path': 'index', 'Navlink': index_navlink}
            self._items.append(DiscourseItem(index_row))

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
            self._items[i].filepath = Path(filepath_string)

            logging.debug(f"DiscourseHandler: __calculate_filepaths: '{self._items[i].filepath}")

    def calculate_item_types(self) -> None:
        """
        Calculates whether each item is a folder, topic, or both (i.e. a header with a landing page)
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
            if not self._items[i].isIndexTopic and (i < len(self._items) - 1):
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

    def download(self) -> None:
        """
        Downloads all topics from their URLs into the paths calculated by :meth:`calculate_filepaths`.
        """
        logging.info("\nCreating directory structure and downloading discourse topics to local markdown files...")
        # 1st pass: Create directory structure
        for item in self._items:
            if item.isFolder:
                full_path = Path(conf['DOCS_LOCAL_PATH']) / item.filepath

                full_path.parent.mkdir(parents=True, exist_ok=True)
                logging.info(f"Created directory '{full_path}'")

        # 2nd pass: Download markdown files into corresponding folders
        for item in self._items:
            logging.debug(
                f"Downloading '{item.title}' to '{item.filepath}' from URL '{item.url}'...")
            full_path = Path(conf['DOCS_LOCAL_PATH']) / item.filepath

            if item.isFolder:
                if not full_path.exists():  # if folder doesn't exist, create.
                    full_path.parent.mkdir(parents=True, exist_ok=True)
            if item.isTopic:
                if item.isFolder:
                    full_path = full_path / full_path.name  # if topic is also a folder, append path so that topic.md gets downloaded into /topic/topic.md
                full_path.parent.mkdir(parents=True, exist_ok=True)  # make sure parents exist
                if full_path.exists(): # if file already exists, remove (TODO: make download method just override)
                    os.remove(full_path)
                download_topic(path=full_path, url=item.url)