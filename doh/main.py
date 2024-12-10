import sys
from discourse_handler import *
from sphinx_handler import *

# docsets that don't work yet (known fix)
multipass = {'instance' : 'discourse.ubuntu.com',
             'home_topic_id' : '8294'} # h1 headers
landscape = {'instance' : 'discourse.ubuntu.com',
             'home_topic_id' : '23070'} # h1 headers
mir = {'instance' : 'discourse.ubuntu.com',
       'home_topic_id' : '27559'} # h1 headers
kafka = {'instance' : 'discourse.charmhub.io',
         'home_topic_id' : '10288', 'generate_h1': False} # [details=Navigation]

# docsets that work as expected
mongodb = {'instance' : 'discourse.charmhub.io',
           'home_topic_id' : '12461', 'generate_h1': False}
opensearch = {'instance' : 'discourse.charmhub.io',
              'home_topic_id' : '9729', 'generate_h1': False}
postgresql = {'instance' : 'discourse.charmhub.io',
              'home_topic_id' : '9710', 'generate_h1': False}

#### input parameters ####
docset = opensearch
docs_local_path = 'docs/'

if __name__ == '__main__':
    """
    Main entry point for the script. Configures logging, sets global config values, and performs the following steps:
    
    1. Download docs from Discourse.
    2. Convert local Discourse docs to Sphinx/RTD (markdown only).
    """
    # TODO (low): Better logging throughout app
    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level=logging.INFO
    )

    # Global config values. See `config.py` for more details.
    conf['DOCS_LOCAL_PATH'] = docs_local_path
    conf['DISCOURSE_INSTANCE'] = docset['instance']
    conf['HOME_TOPIC_ID'] = docset['home_topic_id']
    if not conf['HOME_TOPIC_ID'].isdigit():
        raise ValueError(f"Index topic ID '{conf['HOME_TOPIC_ID']}' contains non-digit characters.")
    conf['GENERATE_H1'] = docset['generate_h1']

    #### Step 1. Download docs from discourse ####
    discourse_docs = DiscourseHandler()

    discourse_docs.calculate_item_type() # determine whether each item is a folder, topic, or both (i.e. heading with/without a landing page)
    
    discourse_docs.calculate_filepaths()  # determine directory structure based on item levels

    discourse_docs.download()

    # #### Step 2. Convert local discourse docs to Sphinx/RTD (markdown only) ####
    sphinx_docs = SphinxHandler(discourse_docs)
    
    sphinx_docs.update_index_pages() # create or rename landing pages as index files

    sphinx_docs.generate_h1_headings() # add h1 heading based on Navlink title

    sphinx_docs.generate_tocs()

    # # TODO (high)
    # sphinx_docs.update_references() # does nothing

    # # TODO (high)
    # sphinx_docs.update_images() # does nothing