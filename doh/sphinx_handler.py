from discourse_handler import *
import glob
import os

class SphinxItem:
    discourse_topic_id : str
    title: str
    path : Path
    ref = ''
    
    def __init__(self, title, filepath, topic_id = '', isHomeTopic = False, isFolder = False, isPage = False):
        self.discourse_topic_id = topic_id

        self.title = title
        self.path = filepath
        self.ref = ''

        self.isHomeTopic = isHomeTopic
        self.isFolder = isFolder
        self.isPage = isPage

class SphinxHandler:

    def __init__(self, discourse_docs: DiscourseHandler):
        self._discourse_docs = discourse_docs

    def update_index_pages(self):
        """
        Ensures there is an index page for each section.

        Rename home page in DOCS_LOCAL_PATH to `index.md`. 
        For each folder, if it has an identically named `.md` file, rename it to `index.md`. Otherwise, create it. 
        """       
        for item in self._discourse_docs._items:           
            if item.isHomeTopic:
                # rename to 'index.md'
                new_path = item.filepath.parent / 'index.md'
                os.rename(item.filepath.with_suffix('.md'), new_path)
                item.update_filepath(new_path)

                logging.info(f"Renamed {item.filepath} to {new_path}")
            if item.isFolder:
                if item.isTopic: 
                    # already has index topic; just need to rename
                    new_path = item.filepath.parent / 'index.md'
                    os.rename(item.filepath.with_suffix('.md'), new_path.with_suffix('.md'))
                    item.update_filepath(new_path)

                    logging.info(f"Renamed {item.filepath} to {new_path}")
                else: 
                    # does not have an index topic, need to create
                    index_file = item.filepath / 'index.md'
                    with open(index_file.with_suffix('.md'), 'w', encoding='utf-8') as f:
                            if conf['GENERATE_H1']:
                                f.write(f"\n")
                            else:
                                f.write(f"# {item.filepath.name.title()}\n")

                    new_item_row = {'Level': '1', 'Path': 'index', 'Navlink': '[Index]()'}
                    new_item = DiscourseItem(new_item_row)
                    new_item.update_filepath(index_file)

                    self._discourse_docs._items.append(new_item)

                    logging.info(f"Created {index_file}.")

    def generate_h1_headings(self, replace_line = True):
        """
        Adds h1 heading to the first line.

        :param: replace_line : If True, replaces the first line of the file (usually author/timestamp).
                If False, prepends before the first line of the file.
        """

        for item in self._discourse_docs._items:
            if item.isTopic:
                    lines = []
                    full_path = item.filepath.with_suffix('.md')
                    with open(full_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    h1_header = ''
                    if item.title == 'index':
                        if item.isHomeTopic:
                            continue
                        # if it's an index page, its h1 header is the name of its parent folder, capitalized
                        h1_header = f"# {item.filepath.parent.name.title()}\n"
                    else:
                        # normal pages use their title property extracted from the Navlink
                        h1_header = f"# {item.title}\n"

                    if replace_line:
                        lines[0] = h1_header
                    else:
                        lines.insert(0, h1_header)

                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    logging.info(f"Added h1 header {h1_header} to {item.filepath}")
                            
    # TODO: add option to customize maxdepth. Currently hardcoded.
    # TODO: use sphinx glob directive instead of doing it myself
    def generate_tocs(self):
        """
        Generate `toctree` for each index file
        """
        logging.info("\nGenerating toctrees for index files...")
        for item in self._discourse_docs._items:
            if item.title == 'index' or item.isHomeTopic:
                parent_path = item.filepath.parent
                toc_list = []
                if item.isHomeTopic:
                    toc_list = glob.glob(f"{parent_path}/*") # all files in docs path (depth 1)
                    for x in toc_list:
                        if '.md' in x:
                            toc_list.remove(x)
                    toc_list = [x.replace(str(parent_path), "") for x in toc_list] # remove parent
                    toc_list = [x + '/index' for x in toc_list] # format
                    toc_list.insert(0, 'self')
                else:
                    toc_list = glob.glob(f"{str(parent_path)}/*") # all files in docs path (depth 1)
                    file_list = []
                    folder_list = []
                    for x in toc_list:
                        if '.md' in x:
                            file_list.append(x)
                        else:
                            x += '/index'
                            folder_list.append(x)

                    toc_list = file_list + folder_list
                    toc_list = [x.replace(conf['DOCS_LOCAL_PATH'], "/") for x in toc_list]
                    toc_list = [x.replace(".md", "") for x in toc_list]

                with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                    f.write("\n```{toctree}\n")
                    f.write(":hidden:\n")
                    f.write(":maxdepth: 2\n\n")
                    for x in toc_list:
                        f.write(f"{x}\n")

                print(f"Created toctree for {item.filepath}")

    def update_references(self):
        """
        Replaces local discourse links with sphinx reference to the equivalent file.

        """
        pass

    def update_images(self):
        pass
