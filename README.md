# discourse-offline-helper (doh)

Features:
* Download discourse documentation locally into markdown files, conserving the navigation structure
* Convert downloaded files into a Sphinx-compatible format. This includes:
  * creating or renaming missing index files
  * replacing hyperlinks to internal discourse pages with the local filepath (e.g. `[Some guide](/t/123)` becomes `[Some guide](how-to/some-guide)`)
  * creating h1 headers if the Discourse pages don't already have them
  * appending a simple toctree to index pages (alphabetical order, `maxdepth 2`)
  * replacing `[note]` admonitions with `{note}` and `[note=caution]` with `{caution}`
* Build Sphinx docs with the built-in starter pack

## Quickstart

The following instructions will show you how to set up your environment, run the script on a small documentation set ([Charmed OpenSearch](https://charmhub.io/opensearch)), and build it locally with the starter pack.

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

When the script has finished running, `cd` into the `docs/` directory and build the starter pack:
```
cd docs/
make run
```
>[!INFO]
> See the [sphinx starter pack's README](https://github.com/canonical/sphinx-docs-starter-pack/blob/main/README.rst) for more information.

## Try it on other doc sets

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

## Configure a new doc set 

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

If True (default), the filename will be `category-a.md`
If False, the filename will be `slug-a.md`

`generate_h1`: Whether or not to generate H1 headers automatically. Only necessary if your pages don't have a h1 header already.

### Documentation requirements

**Navigation table** is wrapped in `[details=Navigation]` and preceded by `# Navigation` h1 heading. 

E.g.
```
# Navigation

[details=Navigation]

| Level   | Path | Navlink |
|---------|------|---------|
| 1 | slug-a   | [Category A](/t/123) |
...

[details=Navigation]
```

**Level**: (WIP - expected level structure)

**Path**: (WIP - can be empty, unless config `use_title_as_filename` is false)

**Navlink**: (WIP)

### Polish or troubleshoot your new Sphinx docs

Once you've run the script and built the HTML docs, you'll probably notice a few things that still need some polishing - maybe some formatting is off or the navigation doesn't show up as expected.

Here's a rough checklist of things to look out for
* `conf.py`: Edit the product title, links, and any other relevant settings
* `index.md` pages: You may want to edit the `toctree`s to reflect a different order or display other titles.
* All markdown pages: Check the formatting.  so it will likely not convert all of the formatting. Certain admonitions and other discourse-flavored markdown elements (i.e. those in `[square brackets][/square brackets]`) might need to be edited manually. Or, you could add more formatting checks to the [`replace_discourse_syntax()`](https://github.com/s-makin/discourse-offline-helper/blob/2d9b233fac16bf1045d07ea008cfe3e8e4b65c5d/doh/sphinx_handler.py#L42) function!
* Links: Check the warnings in the output of the `make run` for a list of links and cross-references that did not process correctly.

## Contribute

`discourse-offline-helper` is still in its early stages, so there's plenty of bugs to find, tests to write, and features to add.

Don't hesitate to raise an [issue on GitHub](https://github.com/s-makin/discourse-offline-helper/issues) or submit a PR! See [CONTRIBUTING.MD](CONTRIBUTING.md) for general contribution guidelines and suggestions. 

To get help or give feedback, please feel free to reach out to `@avgomes` on Mattermost. 