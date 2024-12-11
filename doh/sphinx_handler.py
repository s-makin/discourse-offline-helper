from discourse_handler import *
import os

class SphinxHandler:
    def __init__(self, discourse_docs: DiscourseHandler):
        self._discourse_docs = discourse_docs

    def clean_discourse_metadata(self):
        for item in self._discourse_docs._items:
            if item.isTopic:
                lines = []
                full_path = item.filepath.with_suffix('.md')
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                first_line = lines[0]
                lines.pop(0) # remove first line containing `user | timestamp | #`

                with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                
                logging.debug(f"Removed line '{first_line}' from {item.filepath}")

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
    def generate_tocs(self):
        """
        Generate `toctree` for each index file
        """
        toctree_directives = f"\n```{{toctree}}\n:hidden:\n:titlesonly:\n:maxdepth: 2\n:glob:\n\n"
        logging.info("\nGenerating toctrees for index files...")
        for item in self._discourse_docs._items:
            if item.title == 'index' or item.isHomeTopic:
                if item.isHomeTopic:
                    with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                        f.write(toctree_directives)
                        f.write("self\n")
                        f.write("/tutorial/index\n")
                        f.write("/how-to/index\n")
                        f.write("/reference/index\n")
                        f.write("/explanation/index\n")
                else:
                    with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                        f.write(toctree_directives)
                        f.write("*\n")
                        f.write("*/index\n")

                print(f"Created toctree for {item.filepath}")

    def update_references(self):
        """
        Replaces local discourse links with sphinx reference to the equivalent file.
        """
        pass

    def update_images(self):
        pass
