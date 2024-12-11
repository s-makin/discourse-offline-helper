import argparse
import sys
import yaml
from discourse_handler import *
from sphinx_handler import *

multipass = {'instance' : 'discourse.ubuntu.com',
             'home_topic_id' : '8294', 'generate_h1': True}
landscape = {'instance' : 'discourse.ubuntu.com',
             'home_topic_id' : '23070', 'generate_h1': True}
mir = {'instance' : 'discourse.ubuntu.com',
       'home_topic_id' : '27559', 'generate_h1': True}
ubuntu_core = {'instance' : 'discourse.ubuntu.com',
        'home_topic_id' : '19764', 'generate_h1': True}
snap = {'instance' : 'forum.snapcraft.io',
      'home_topic_id' : '11127', 'generate_h1': True}
kafka = {'instance' : 'discourse.charmhub.io',
         'home_topic_id' : '10288', 'generate_h1': False} # needs [details=Navigation]
mongodb = {'instance' : 'discourse.charmhub.io',
           'home_topic_id' : '12461', 'generate_h1': False}
opensearch = {'instance' : 'discourse.charmhub.io',
              'home_topic_id' : '9729', 'generate_h1': False}
postgresql = {'instance' : 'discourse.charmhub.io',
              'home_topic_id' : '9710', 'generate_h1': False}

#### input parameters ####
docset = opensearch
docs_local_path = '/home/andreia/Documents/code/pdf-test-repo/docs/'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='discourse-offline-helper',
                                     description='Download Discourse docs and convert to Sphinx/RTD markdown.')
    parser.add_argument('-docset', type=str, help='Discourse documentation to download. See config.yaml for options.')
    parser.add_argument('--docs_directory', type=str, help='Local path to save the downloaded docs.', default='docs/')
    parser.add_argument('--debug', type=str, help='Increase log verbosity', default=False)
    
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
    with open('doh/config.yaml') as config_file:
        config = yaml.safe_load(config_file)

    config = config[args.docset]
    config['docs_directory'] = args.docs_directory

    #### Step 1. Download docs from discourse ####
    discourse_docs = DiscourseHandler(config)

    discourse_docs.calculate_item_type()
    discourse_docs.calculate_filepaths()
    discourse_docs.download()

    # #### Step 2. Convert local discourse docs to Sphinx/RTD (markdown only) ####
    sphinx_docs = SphinxHandler(discourse_docs, config)

    sphinx_docs.remove_discourse_metadata()
    sphinx_docs.replace_discourse_syntax() 
    sphinx_docs.update_links()
    sphinx_docs.update_index_pages() # create or rename landing pages as index files
    if config['generate_h1']:
        sphinx_docs.generate_h1_headings() # add h1 heading based on Navlink title
    sphinx_docs.generate_tocs()