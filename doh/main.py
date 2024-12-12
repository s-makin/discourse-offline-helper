import argparse
import sys
import yaml
import shutil
from discourse_handler import *
from sphinx_handler import *

CONFIG_FILE = 'doh/config.yaml'

test_navtable = \
"""[details=Navigation]

| Level | Path | Navlink |
|-------|------|---------|
| 1 | tutorial | [Tutorial](/t/9722) |
| 2 | t-set-up | [1. Set up the environment](/t/9724) |
| 1 | how-to | [How To]() |
| 2 | h-deploy | [Deploy]() |
| 3 | h-deploy-lxd | [Deploy on LXD](/t/14575) |
| 2 | h-tls| [TLS encryption](/t/14783) |
| 3 | h-rotate-tls-ca-certificates   | [Rotate TLS/CA certificates](/t/15422) |
| 1 | test | |
|  | test2 | |
[/details]"""

test_result = \
"""
{'Level': '1', 'Path': 'tutorial', 'Navlink': '[Tutorial](/t/9722)'}
{'Level': '2', 'Path': 't-set-up', 'Navlink': '[1. Set up the environment](/t/9724)'}
{'Level': '1', 'Path': 'how-to', 'Navlink': '[How To]()'}
{'Level': '2', 'Path': 'h-deploy', 'Navlink': '[Deploy]()'}
{'Level': '3', 'Path': 'h-deploy-lxd', 'Navlink': '[Deploy on LXD](/t/14575)'}
{'Level': '2', 'Path': 'h-tls', 'Navlink': '[TLS encryption](/t/14783)'}
{'Level': '3', 'Path': 'h-rotate-tls-ca-certificates', 'Navlink': '[Rotate TLS/CA certificates](/t/15422)'}
{'Level': '1', 'Path': 'test', 'Navlink': ''}
{'Level': '', 'Path': 'test2', 'Navlink': ''}
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='discourse-offline-helper',
                                     description='Download Discourse docs and convert to Sphinx/RTD markdown.')
    parser.add_argument('-docset', type=str, help='Discourse documentation to download. See config.yaml for options.')
    parser.add_argument('--docs_directory', type=str, help='Local path to save the downloaded docs.', default='docs/src/')
    parser.add_argument('--debug', type=str, help='Increase log verbosity', default=False)
    
    args = parser.parse_args()

    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level= logging.DEBUG #logging_level
    )

    # Load config.yaml and extract data
    with open(CONFIG_FILE) as config_file:
        config = yaml.safe_load(config_file)

    config = config[args.docset]
    config['docs_directory'] = args.docs_directory

    # Delete existing docs directory
    if config['docs_directory'] == 'docs/src' and os.path.exists(config['docs_directory']):
        shutil.rmtree(config['docs_directory'])

    # Download and process a Discourse documentation set 
    discourse_docs = DiscourseHandler(config)

    discourse_docs.calculate_item_type() # determine if item is a folder, page, or both
    discourse_docs.calculate_filepaths() # calculate local file paths
    discourse_docs.download() # download raw markdown files from Discourse

    # Convert local discourse docs to a Sphinx/RTD-compatible format (markdown only)
    sphinx_docs = SphinxHandler(discourse_docs, config)

    sphinx_docs.remove_discourse_metadata() # remove timestamp and comments
    sphinx_docs.replace_discourse_syntax() # replace [note] admonitions
   
    sphinx_docs.update_index_pages() # create or rename landing pages as index files

    sphinx_docs.update_links() # replace discourse links with local file paths
    if config['generate_h1']:
        sphinx_docs.generate_h1_headings() # add h1 heading based on 'Navlink' text
    sphinx_docs.generate_tocs() # generate toctree for each index file