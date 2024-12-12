import argparse
import sys
import yaml
from discourse_handler import *
from sphinx_handler import *

CONFIG_FILE = 'doh/config.yaml'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='discourse-offline-helper',
                                     description='Download Discourse docs and convert to Sphinx/RTD markdown.')
    parser.add_argument('--docset', type=str, help='Discourse documentation to download. See config.yaml for options.')
    parser.add_argument('--docs_directory', type=str, help='Local path to save the downloaded docs.', default='docs/src/')
    parser.add_argument('--debug', action="store_true", help="Log verbosity")

    args = parser.parse_args()

    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level=logging_level
    )

    # Load config.yaml and extract data
    with open(CONFIG_FILE) as config_file:
        config = yaml.safe_load(config_file)

    config = config[args.docset]
    config['docs_directory'] = args.docs_directory

    # Download and process a Discourse documentation set 
    discourse_docs = DiscourseHandler(config)

    discourse_docs.calculate_item_type() # determine if item is a folder, page, or both
    discourse_docs.calculate_filepaths() # calculate local file paths
    discourse_docs.download() # download raw markdown files from Discourse

    # Convert local discourse docs to a Sphinx/RTD-compatible format (markdown only)
    sphinx_docs = SphinxHandler(discourse_docs, config)

    sphinx_docs.remove_discourse_metadata() # remove timestamp and comments
    sphinx_docs.replace_discourse_syntax() # replace [note] admonitions
    sphinx_docs.update_links() # replace discourse links with local file paths
    sphinx_docs.update_index_pages() # create or rename landing pages as index files
    if config['generate_h1']:
        sphinx_docs.generate_h1_headings() # add h1 heading based on 'Navlink' text
    sphinx_docs.generate_tocs() # generate toctree for each index file