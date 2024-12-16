import argparse
import yaml
import shutil
from .sphinx_handler import *

CONFIG_FILE = 'doh/config.yaml'

def launch():

    parser = argparse.ArgumentParser(prog='discourse-offline-helper',
                                     description='Download Discourse docs and convert to Sphinx/RTD markdown.')
    parser.add_argument('--docset', type=str, help='Discourse documentation to download. See config.yaml for options.')
    parser.add_argument('--docs_directory', type=str, help='Local path to save the downloaded docs. Default is docs/src/', default='docs/src/')
    parser.add_argument('--debug', action="store_true", help="Increase log verbosity")

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

    if args.docset not in config:
        logging.error(f"ERROR: Documentation set '{args.docset}' not found in config.yaml. Exiting program.")
        sys.exit(1)

    config = config[args.docset]
    config['docs_directory'] = args.docs_directory

    # Uncomment to delete the existing docs directory each time the script is run
    # if os.path.exists(args.docs_directory):
    #     shutil.rmtree(args.docs_directory)
        
    # Download and process a Discourse documentation set 
    discourse_docs = DiscourseHandler(config)

    discourse_docs.calculate_item_type() # determine if item is a folder, page, or both
    discourse_docs.calculate_filepaths() # calculate local file paths
    discourse_docs.download() # download raw markdown files from Discourse

    # Convert local discourse docs to a Sphinx/RTD-compatible format (markdown only)
    sphinx_docs = SphinxHandler(discourse_docs, config)

    sphinx_docs.update_index_pages() # create or rename landing pages as index files
    sphinx_docs.update_links() # replace discourse links with local file paths
    sphinx_docs.replace_discourse_metadata(truncate_comments=True) # remove timestamp and comments, adds h1 headings.
    sphinx_docs.replace_discourse_notes() # replace [note] admonitions
    sphinx_docs.generate_tocs() # generate toctree for each index file