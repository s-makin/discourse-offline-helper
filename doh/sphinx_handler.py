from discourse_handler import *
import os

class SphinxHandler:
    def __init__(self, discourse_docs: DiscourseHandler, configuration: dict) -> None:
        self.config = configuration

        self._discourse_docs = discourse_docs

    def remove_discourse_metadata(self):
        """
        Removes timestamp and comments from the discourse topics.
        
        The metadata on the first line is in the format `user | timestamp | #`.
        The comments are expected to be separated by a delimiter `-------------------------`.

        :raises ValueError: If the file is empty.
        """
        for item in self._discourse_docs._items:
            if item.isTopic:
                lines = []
                with open(item.filepath.with_suffix('.md'), 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if len(lines) == 0:
                    raise ValueError(f"File {item.filepath} is empty.")
                
                # remove all lines after the delimiter in case there are comments
                content_before_comments = []
                comment_delimiter = '-------------------------\n'
                if item.isHomeTopic:
                    comment_delimiter = '## Navigation\n'
                for line in lines:
                    if comment_delimiter in line:
                        break
                    content_before_comments.append(line)

                if content_before_comments:
                    lines = content_before_comments
                else:
                    logging.debug(f"Did not find comment delimiter in {item.filepath}")
                
                # remove first line containing `user | timestamp | #`
                lines.pop(0)
                
                with open(item.filepath.with_suffix('.md'), 'w', encoding='utf-8') as f:
                        f.writelines(content_before_comments)

    def replace_discourse_syntax(self):
        """
        Replaces markdown elements with Discourse syntax (i.e. square brackets) and replaces them with Sphinx/RTD or regular markdown equivalents.
        
        The following replacements are made:
        * [note] [/note] -> ```{note}
        * more replacements to be implemented
        """
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
        for item in self._discourse_docs._items:           
            if item.isHomeTopic and item.filename != 'index':
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
                            if self.config['generate_h1']:
                                f.write(f"\n")
                            else:
                                f.write(f"# {item.filepath.name.title()}\n")
                    
                    title = item.filepath.name.title()
                    new_item_row = {'Level': '1', 'Path': 'index', 'Navlink': f'[{title}]()'}
                    new_item = DiscourseItem(new_item_row, self.config)
                    new_item.update_filepath(index_file)

                    self._discourse_docs._items.append(new_item)

                    logging.info(f"Created {index_file}.")

    def __link_replacement(self, match):
        text = match.group(1)
        topic_id = match.group(2)
        
        new_value = ''
        for item in self._discourse_docs._items:
            if item.topic_id == topic_id:
                new_value = item.filepath.relative_to(self.config['docs_directory'])
        
        return f"[{text}](/{new_value})"

    def update_links(self):
        """
        Replaces local discourse links with local path to the equivalent file.
        """
        for item in self._discourse_docs._items:
            if item.isTopic:
                lines = []
                with open(item.filepath.with_suffix('.md'), 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                updated_lines = []
                pattern = r"\[([^\]]+)]\(/t/[^)]*?(\d+)\)" # Matches [<text>](/t/<id>)
                for line in lines:
                    new_line = re.sub(pattern, self.__link_replacement, line)
                    updated_lines.append(new_line)

                with open(item.filepath.with_suffix('.md'), 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
            
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
                            
    def generate_tocs(self):
        """
        Generate `toctree` for each index file
        """

        toctree_directives = f"\n```{{toctree}}\n:hidden:\n:titlesonly:\n:maxdepth: 2\n:glob:\n\n"
        
        logging.info("\nGenerating toctrees for index files...")
        for item in self._discourse_docs._items:
            if item.title == 'index':
                if item.isHomeTopic:
                    with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                        f.write(toctree_directives)
                        f.write("self\n")
                        f.write("/tutorial*/index\n")
                        f.write("/how*/index\n")
                        f.write("/reference*/index\n")
                        f.write("/explanation*/index\n")
                        f.close()
                else:
                    with open(item.filepath.with_suffix('.md'), 'a', encoding='utf-8') as f:
                        f.write(toctree_directives)
                        f.write("*\n")
                        f.write("*/index\n")
                        f.close()

                print(f"Created toctree for {item.filepath}")

