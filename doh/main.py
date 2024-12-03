import sys
from discourse_handler import *
from sphinx_handler import *

# docsets that don't work yet (known fix)
multipass = {'instance' : 'discourse.ubuntu.com',
             'index_topic_id' : '8294'} # h1 headers
landscape = {'instance' : 'discourse.ubuntu.com',
             'index_topic_id' : '23070'} # h1 headers
mir = {'instance' : 'discourse.ubuntu.com',
       'index_topic_id' : '27559'} # h1 headers
kafka = {'instance' : 'discourse.charmhub.io',
         'index_topic_id' : '10288'} # [details=Navigation]

# docsets that work as expected
mongodb = {'instance' : 'discourse.charmhub.io',
           'index_topic_id' : '12461'}
opensearch = {'instance' : 'discourse.charmhub.io',
              'index_topic_id' : '9729'}
postgresql = {'instance' : 'discourse.charmhub.io',
              'index_topic_id' : '9710'}

#### input parameters ####
docset = opensearch
docs_local_path = 'docs/'

if __name__ == '__main__':

    # TODO (low): Better logging throughout app
    logging.basicConfig(
        stream=sys.stdout,
        format="%(message)s",
        level=logging.INFO
    )

    # Global config values. See `config.py` for more details.
    conf['DOCS_LOCAL_PATH'] = docs_local_path
    conf['DISCOURSE_INSTANCE'] = docset['instance']
    conf['INDEX_TOPIC_ID'] = docset['index_topic_id']
    if not conf['INDEX_TOPIC_ID'].isdigit():
        raise ValueError(f"Index topic ID '{conf['INDEX_TOPIC_ID']}' contains non-digit characters.")
    conf['USE_TITLE_AS_FILENAME'] = True
    
    #### Step 1. Download docs from discourse ####
    discourse_docs = DiscourseHandler()

    discourse_docs.calculate_filepaths()  # first, determine directory structure based on item levels
    discourse_docs.calculate_item_types() # then, determine whether each item is a folder, topic, or both (i.e. heading with/without a landing page)

    discourse_docs.download()

    #### Step 2. Convert local discourse docs to Sphinx/RTD (markdown only) ####
    sphinx_docs = SphinxHandler(discourse_docs)
    
    # This is disabled because there's a known bug (will likely crash)
    # sphinx_docs.generate_target_ids()

    sphinx_docs.generate_tocs()

    # TODO (high)
    sphinx_docs.update_references() # does nothing

    # TODO (high)
    sphinx_docs.update_images() # does nothing