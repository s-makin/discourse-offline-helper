from discourse_handler import *
import glob
import os

class SphinxItem:
    discourse_topic_id : str
    discourse_title: str
    path : Path
    ref = ''
    
    def __init__(self, title, filepath, topic_id = '', isIndexTopic = False):
        self.discourse_topic_id = topic_id
        self.discourse_title = title

        self.path = filepath
        self.ref = ''

        self.isIndexTopic = isIndexTopic

class SphinxHandler:
    
    # Initialize from discourse docs
    def __init__(self, discourse_docs: DiscourseHandler):
        self._discourse_docs = discourse_docs

        # TODO (med): expose these private methods with a generate_index_pages() function for more transparency
        self.__create_index_pages() 
        self.__generate_items_list()

    def __create_index_pages(self):
        """
        Ensures there is an index page for each section.

        First, rename home page in DOCS_LOCAL_PATH to `index.md`. 
        Then, for each folder, if isTopic, rename the `.md` file to `index.md`.

        TODO: add diataxis section property to SphinxItem? avoid long ids
        TODO: discard empty rows
        """
        logging.info("\nCreating missing index pages...")
        for item in self._discourse_docs._items:
            if item.isIndexTopic:
                old_path = Path(conf['DOCS_LOCAL_PATH']) / item.filepath
                new_path = old_path.parent / 'index'
                os.rename(old_path.with_suffix('.md'), new_path.with_suffix('.md'))

                updated_filepath = str(new_path)
                updated_filepath = updated_filepath.replace(conf['DOCS_LOCAL_PATH'], "")
                item.update_filepath(Path(updated_filepath))
                logging.info(f"Renamed {old_path} to {new_path}")
            if item.isFolder:
                if item.isTopic:
                    filepath = Path(conf['DOCS_LOCAL_PATH']) / item.filepath
                    old_path = filepath / filepath.name 
                    new_path = old_path.parent / 'index'
                    os.rename(old_path.with_suffix('.md'), new_path.with_suffix('.md'))
                    logging.info(f"Renamed {old_path} to {new_path}")

                    # Ugly things we gotta do because paths are poorly handled rn
                    updated_filepath = str(new_path)
                    updated_filepath = updated_filepath.replace(conf['DOCS_LOCAL_PATH'], "")
                    item.update_filepath(Path(updated_filepath))
                else:
                    index_file = conf['DOCS_LOCAL_PATH'] / Path(item.filepath) / 'index'
                    with open(index_file.with_suffix('.md'), 'w', encoding='utf-8') as f:
                        f.write(f"\n\n# {item.title.title()}")
                    logging.info(f"Created {index_file}.")

                    new_item_row = {'Level': '1', 'Path': 'index', 'Navlink': '[Index]()'}
                    new_item = DiscourseItem(new_item_row)

                    updated_filepath = str(index_file)
                    updated_filepath = updated_filepath.replace(conf['DOCS_LOCAL_PATH'], "")
                    new_item.update_filepath(Path(updated_filepath))

                    self._discourse_docs._items.append(new_item)

    def __generate_items_list(self):
        self.sphinx_items = []
        for item in self._discourse_docs._items:
            if item.isTopic:
                path = Path(conf['DOCS_LOCAL_PATH']) / item.filepath

                sphinx_item = SphinxItem(item.title, path.with_suffix('.md'), item.topic_id, item.isIndexTopic)
                self.sphinx_items.append(sphinx_item)

    # TODO (high): fix path bug
    # TODO (low): fix some small inconsistencies in the generation (e.g. unwanted symbols)
    # TODO (low): add config option to disable or customize
    def generate_target_IDs(self):
        """
        Generates `target_id`.

        For each `.md` file, create a `target_id` based on filepath.
        E.g. how-to/deploy.md -> (howto-deploy)=
        E.g. reference/commands/deploy.md -> (reference-commands-deploy)=
        """
        for item in self.sphinx_items:
            
            path_parts = item.path.parts
            if path_parts[-1] == 'index':
                if len(path_parts) == 1: # top level index page is home
                    item.ref = 'home'
                else:
                    item.ref = slugify(path_parts[-2]) # id for index pages is parent folder name
            else:
                item.ref = '-'.join(path_parts) # id for regular page is full path
            
            target_id = f"({item.ref})=\n"        

            lines = []
            full_path = item.path.with_suffix('.md')
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if lines:
                lines[0] = target_id
            else:
                lines = target_id
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

    # TODO(low): add option to customize maxdepth. Currently hardcoded.
    # TODO(med): Fix inclusion of index files
    def generate_tocs(self):
        """
        Generate `toctree` for each index file
        """
        logging.info("\nGenerating toctrees for index files...")
        for item in self.sphinx_items:
            if item.discourse_title == 'index' or item.isIndexTopic:
                parent_path = item.path.parent
                toc_list = []
                if item.isIndexTopic:
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

                with open(item.path.with_suffix('.md'), 'a', encoding='utf-8') as f:
                    f.write("\n```{toctree}\n")
                    f.write(":hidden:\n")
                    f.write(":maxdepth: 2\n\n")
                    for x in toc_list:
                        f.write(f"{x}\n")

                print(f"Created toctree for {item.path}")

    def update_references(self):
        """
        Replaces local discourse links with sphinx reference to the equivalent file.

        """
        pass

    def update_images(self):
        pass
