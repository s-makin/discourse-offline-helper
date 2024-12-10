"""
GLOBAL CONFIG VALUES (TODO: use YAML instead)

`DOCS_LOCAL_PATH`
Target folder for downloaded docs. Relative to the script's directory, or absolute.

`DISCOURSE_INSTANCE`
Discourse instance without 'http:://'

`HOME_TOPIC_ID`
Index/overview topic ID without '/t/'

This would be the discourse topic that contains the Navigation table.

`USE_TITLE_AS_FILENAME`
Filenames can get generated with the navtable 'Path' or with the title extracted from the 'Navlink'.

E.g. 
| Level   | Path | Navlink |
|---------|------|---------|
| 1 | slug-a   | [Category A](/t/123) |

if USE_TITLE_AS_FILENAME = True (default), the filename will be `category-a.md`
if USE_TITLE_AS_FILENAME = False, the filename will be `slug-a.md`

`GENERATE_H1`
Generates H1 headers automatically if True.
"""

default_docs_local_path = 'docs/'
default_discourse_instance = 'discourse.charmhub.io'
default_home_topic_id = '9729'
default_use_title = True
default_generate_h1 = True

conf = {'DOCS_LOCAL_PATH': default_docs_local_path,
        'DISCOURSE_INSTANCE': default_discourse_instance,
        'HOME_TOPIC_ID': default_home_topic_id,
        'USE_TITLE_AS_FILENAME': default_use_title,
        'GENERATE_H1': default_generate_h1}