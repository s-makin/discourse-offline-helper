# discourse-offline-helper (doh)

> [!NOTE]
> This is under active development and is not ready for general use.
> 
> If you are interested, please get in touch with Andreia Velasco! (@avgomes on Mattermost)

The `doh` module:
* Downloads discourse documentation locally into markdown files, conserving the navigation structure
* Converts downloaded documentation into a Sphinx-compatible format. This includes:
  * creating or renaming missing index files
  * replacing hyperlinks to internal discourse pages with the local filepath (e.g. `[Some guide](/t/123)` becomes `[Some guide](how-to/some-guide)`)
  * creating h1 headers if the Discourse pages don't already have them
  * appending a simple toctree to index pages (alphabetical order, `maxdepth 2`)

## demo
The following instructions will show you how to set up your environment and run the script on a small documentation set ([Charmed OpenSearch](https://charmhub.io/opensearch)) into a local `'/docs'` folder:

Clone the repo and enter its root directory:
```
git clone git@github.com:a-velasco/offline-helper.git
cd offline-helper
```

Start a virtual environment (called `demo` in the commands below):
```
python3 -m venv demo
source demo/bin/activate
```
Install dependencies:
```
python3 -m pip install -r requirements.txt
```
Run `doh/main.py`
```
python3 doh/main.py -docset opensearch
```

## try it on other doc sets

There are currently several pre-configured Discourse documentation sets that can be passed in as `-docset` arguments:
* `multipass`
* `landscape`
* `mir`
* `ubuntu_core`
* `snap`
* `kafka`
* `mongodb`
* `opensearch`
* `postgresql`

## configure a new doc set 

To edit an existing doc set or create a new one, see the [`config.yaml`](doh/config.yaml) file.

### `config.yaml` parameters

`discourse_instance`: Discourse instance without 'http://'

`home_topic_id`: Index/overview/home topic ID without '/t/'
This would be the discourse topic that contains the Navigation table.

`use_title_as_filename`: Determines whether filenames get generated with the navtable 'Path' or with the title extracted from the 'Navlink'.
E.g. 
| Level   | Path | Navlink |
|---------|------|---------|
| 1 | slug-a   | [Category A](/t/123) |

if True (default), the filename will be `category-a.md`
if False, the filename will be `slug-a.md`

`generate_h1`: Whether or not to generate H1 headers automatically. 
Only necessary if your pages don't have a h1 header already.