from discourse_handler import *
import os

class SphinxHandler:
    def __init__(self, discourse_docs: DiscourseHandler, configuration: dict) -> None:
        self.config = configuration

        self._discourse_docs = discourse_docs

    def replace_discourse_metadata(self, truncate_comments: bool = True, custom_delimiter: str = None):
        """
        Removes timestamp and (optionally) comments. Adds MyST heading target and a H1 heading.
        
        The metadata on the first line is in the format `user | timestamp | #`.
        The comments are expected to be separated by a delimiter `-------------------------`.
        For the home page, the delimiter is `# Navigation`.
        """
        logging.info("\nRemoving Discourse metadata...")
        for item in self._discourse_docs._items:
            if item.isTopic:
                lines = []
                with open(item.filepath.with_suffix('.md'), 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if len(lines) == 0:
                    logging.error(f"ERROR: File {item.filepath} is empty. Exiting program.")
                    continue
            
                # replace first line with autogenerated MyST heading target `(path-from-root)=`
                # first line contains `user <username> | <timestamp> | #<number>`, which should be removed anyway
                myst_target = slugify(str(item.filepath.relative_to(self.config['docs_directory']).with_suffix('')))
                lines[0] = f"({myst_target})=\n"

                # add h1 heading
                if self.config['generate_h1']:
                    h1_heading = ''
                    if item.title == 'index':
                        if item.isHomeTopic:
                            return
                        # non-root index pages use the name of their parent folder
                        h1_heading = f"# {item.filepath.parent.name.title()}\n"
                    else:
                        # normal pages use their title property extracted from the Navlink
                        h1_heading = f"# {item.title}\n"
                    lines.insert(1, h1_heading)
                
                # ensure third line is empty
                if len(lines) >= 3 and lines[2] != '\n':
                    lines.insert(2, '\n')

                # remove all lines after the `comment_delimiter`
                if truncate_comments:
                    content_before_comments = []
                    comment_delimiter = '-------------------------\n'
                    if custom_delimiter:
                        comment_delimiter = custom_delimiter
                    elif item.isHomeTopic:
                        comment_delimiter = '# Navigation'
                    
                    for line in lines:
                        if comment_delimiter in line:
                            break
                        content_before_comments.append(line)

                    lines = content_before_comments

                with open(item.filepath.with_suffix('.md'), 'w', encoding='utf-8') as f:
                        f.writelines(content_before_comments)

    def replace_discourse_syntax(self):
        """
        Replaces markdown elements with Discourse syntax (i.e. square brackets) and replaces them with Sphinx/RTD or regular markdown equivalents.
        
        The following replacements are made:
        * [note] [/note] -> ```{note}
        * more replacements to be implemented
        """
        logging.info("\nReplacing discourse markdown syntax...")
        for item in self._discourse_docs._items:
            if item.isTopic:
                lines = []
                with open(item.filepath.with_suffix('.md'), 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                updated_lines = []
                for line in lines:
                    line = re.sub(r'\[note.*?caution.*?\]', r'```{caution}', line)  # Matches [note="caution"] and replaces with ```{caution}
                    line = re.sub(r'\[note\]', r'```{note}', line)  # Matches [note] and replaces with ```{note}
                    line = re.sub(r'\[/note\]', r'```', line)  # Matches [/note] and replaces with ```

                    updated_lines.append(line)

                with open(item.filepath.with_suffix('.md'), 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)

    def update_index_pages(self):
        """
        Ensures there is an index page for each section.

        Rename home page in docs_local_path to `index.md`. 
        For each folder, if it has an identically named `.md` file, rename it to `index.md`. Otherwise, create it. 
        """
        logging.info("\nUpdating index pages...")

        for item in self._discourse_docs._items:           
            if item.isHomeTopic:
                # rename to 'index.md'
                new_path = item.filepath.parent / 'index'
                os.rename(item.filepath.with_suffix('.md'), new_path.with_suffix('.md'))
                item.update_filepath(new_path)

                logging.debug(f"Renamed {item.filepath} to {new_path}")
            if item.isFolder:
                if item.isTopic: 
                    # already has index topic; just need to rename
                    new_path = item.filepath.parent / 'index.md'
                    os.rename(item.filepath.with_suffix('.md'), new_path.with_suffix('.md'))
                    item.update_filepath(new_path)

                    logging.debug(f"Renamed {item.filepath} to {new_path}")
                else: 
                    # does not have an index topic, need to create
                    index_file = item.filepath / 'index.md'
                    with open(index_file.with_suffix('.md'), 'w', encoding='utf-8') as f:
                            if self.config['generate_h1']: # special handling for new index files
                                f.write(f"\n")
                            else:
                                f.write(f"\n# {item.filepath.name.title()}\n")

                    new_item_row = {'Level': '1', 'Path': 'index', 'Navlink': '[Index]()'}
                    new_item = DiscourseItem(new_item_row, self.config)
                    new_item.update_filepath(index_file)

                    self._discourse_docs._items.append(new_item)

                    logging.info(f"Created {index_file}.")

    def __generate_h1_heading(self, item):

        if item.isTopic:
                h1_heading = ''
                if item.title == 'index':
                    if item.isHomeTopic:
                        return
                    # if it's an index page, its h1 header is the name of its parent folder, capitalized
                    h1_heading = f"# {item.filepath.parent.name.title()}\n"
                else:
                    # normal pages use their title property extracted from the Navlink
                    h1_heading = f"# {item.title}\n"
                
                return h1_heading

    def __link_replacement(self, match):
        text = match.group(1)
        topic_id = match.group(2)
        
        new_value = ''
        for item in self._discourse_docs._items:
            if item.topic_id == topic_id:
                new_value = item.filepath.relative_to(self.config['docs_directory']).with_suffix('')
        
        return f"[{text}](/{new_value})"

    def update_links(self):
        """
        Replaces local discourse links with local path to the equivalent file.
        """
        logging.info("\nUpdating internal links...")
        for item in self._discourse_docs._items:
            if item.isTopic:
                lines = []
                if not item.filepath.with_suffix('.md').exists():
                    logging.error(f"ERROR: File {item.filepath} not found. Exiting program")
                    sys.exit(1)
                with open(item.filepath.with_suffix('.md'), 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                updated_lines = []
                pattern = r"\[([^\]]+)]\(/t/[^)]*?(\d+)\)"
                for line in lines:
                    new_line = re.sub(pattern, self.__link_replacement, line)
                    updated_lines.append(new_line)

                with open(item.filepath.with_suffix('.md'), 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)

    def generate_tocs(self):
        """
        Generate `toctree` for each index file
        """
        logging.info("\nGenerating toctrees for index files...")

        toctree_directives = f"\n```{{toctree}}\n:hidden:\n:titlesonly:\n:maxdepth: 2\n:glob:\n\n"
        for item in self._discourse_docs._items:
            if item.title == 'index' or item.isHomeTopic:
                if item.isHomeTopic:
                    with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                        f.write(toctree_directives)
                        f.write("Home <self>\n")
                        f.write("/tutorial*/index\n")
                        f.write("/how*/index\n")
                        f.write("/reference*/index\n")
                        f.write("/explanation*/index\n")
                        f.write("*\n")
                else:
                    with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                        f.write(toctree_directives)
                        f.write("*\n")
                        f.write("*/index\n")

                print(f"Created toctree for {item.filepath}")

