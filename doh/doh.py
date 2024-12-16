import argparse
import shutil
from .sphinx_handler import *

def launch():

    parser = argparse.ArgumentParser(prog='discourse-offline-helper',
                                     description='Download Discourse docs and convert to Sphinx/RTD markdown.')
    parser.add_argument('-i', '--instance', type=str, help="Discourse instance to download from. E.g. 'discourse.ubuntu.com'", required=True)
    parser.add_argument('-h', '--home_topic_id', type=str, help='Topic ID of home page containing navigation table.', required=True)
    parser.add_argument('-d', '--docs_directory', type=str, help='Local path to save the downloaded docs. Default is docs/src/', default='docs/src/')
    parser.add_argument('--generate_h1', action="store_true", help='Generate h1 headings from topic titles.')
    parser.add_argument('--debug', action="store_true", help="Increase log verbosity")

    args = parser.parse_args()

    config = {}
    instance = args.instance
    if '://' in instance:
        instance = instance.split('://')[1]
    if 'www.' in instance:
        instance = instance.split('www.')[1]
    config['instance'] = args.instance

    home_topic_id = args.home_topic_id
    if not home_topic_id.isdigit():
        sys.exit("ERROR: --home_topic_id must be a number. E.g. '1234'.")
    config['home_topic_id'] = args.home_topic_id

    config['generate_h1'] = args.generate_h1

    config['docs_directory'] = args.docs_directory

    logging_level = logging.INFO
    if args.debug: 
        logging_level = logging.DEBUG
    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level=logging_level     
    )

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