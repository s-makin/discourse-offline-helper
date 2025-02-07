# discourse-offline-helper (doh)

_Downloads a Discourse documentation set and prepares it for PDF generation with the Canonical Sphinx starter pack._

> [!WARNING]
> This tool is under active development and not fully stable.
> If you'd like to troubleshoot or customize this tool for a particular doc set, don't hesitate to contact `@avgomes` on Mattermost.

## Features
* Downloads raw markdown files locally
* Creates missing index files
* Replaces discourse cross-references with the local filepath (e.g. `[Some guide](/t/123)` becomes `[Some guide](how-to/some-guide)`)
* Creates h1 headers if the Discourse pages don't already have them
* Appends a simple toctree to index pages (alphabetical order, `maxdepth 2`)
* Replaces `[note]` discourse syntax

<details>

<summary>Planned</summary>

* Fix issue with cross-referencing other headings ([#17](https://github.com/s-makin/discourse-offline-helper/issues/17))
* Improve the UI
    * add option to use text file with navtable as the input ([#18](https://github.com/s-makin/discourse-offline-helper/issues/18))
    * make function sequences and dependencies more transparent
    * snap the `doh` module to remove python requirement (`sudo snap install doh & doh -docset <product>`) ([#20](https://github.com/s-makin/discourse-offline-helper/issues/20))
* Automatically replace `[tab]` discourse syntax ([#21](https://github.com/s-makin/discourse-offline-helper/issues/20))
* Automatically replace `<href>` anchors with regular markdown headings ([#22](https://github.com/s-makin/discourse-offline-helper/issues/22))
* Features for PDF generation
* ...

</details>

## Quickstart

To run the script, you must either: 
- configure a Python 3 environment with the dependencies in `requirements.txt` installed
- or [download the executable](https://github.com/s-makin/discourse-offline-helper/releases/tag/v0.0.1) (currently only for Ubuntu 24.04 on amd64)

To convert a sample documentation set on Discourse ([Charmed OpenSearch](https://charmhub.io/opensearch)), run
```
# Python module
python3 -m doh -i discourse.charmhub.io -t 9729 --generate_h1

# Executable (on Ubuntu 24.04)
./doh -i discourse.charmhub.io -t 9729 --generate_h1
```
> use the `--debug` flag for more detailed logs

`cd` into the `docs/` directory and build the starter pack:
```
cd docs/
make run
```
> [!TIP]
> See the [sphinx starter pack's README](https://github.com/canonical/sphinx-docs-starter-pack/blob/main/README.rst) for more information.

### Try it on other doc sets

`doh` takes the following arguments:
* `-i`, `--instance`: Discourse instance to download from. E.g. `discourse.ubuntu.com`
* `-t`, `--home_topic_id`: Topic ID of home page containing navigation table. E.g. `123`
* `--generate_h1`: Generate h1 headings from topic titles. Use this flag if the **raw markdown** of your docs doesn't contain the title in a H1 header
* (Optional) `-d`, `--docs_directory`: Local path to save the downloaded docs. Default is `docs/src/`.
* (Optional) `--navtable`: Path to a .md or .txt file with a custom navigation table. Use this option if you need to restructure your navtable to fulfill the [Documentation requirements](#documentation-requirements).
* (Optional) `--debug`: Increase log verbosity

### Documentation requirements

This tool takes into account several common variations between different Discourse sets, but not all. For it to work as smoothly as possible, the documentation set must fulfill a few requirements.

> [!TIP]
> This tool was intentionally built to be modular and adaptable, so if any of those requirements don't work for you, please submit an issue or contact @avgomes on Mattermost so we can customize the behavior of the tool for you.

#### Navigation table requirements

**Requirement**: (mandatory) The navigation table is wrapped in `[details=Navigation]`. 
```
[details=Navigation]

| Level   | Path | Navlink |
|---------|------|---------|
| 1 | slug-a   | [Category A](/t/123) |
...

[details=Navigation]
```

There will soon be an option to wrap it in a comment instead, or use a text file containing your navtable.

**Requirement**: (mandatory) If you have Level 0 items, they must be standalone pages, like the Home page. **They must not be parent folders**, such as the Diataxis sections.

Example of a valid navigation table structure:
```
    | Level   | Path | Navlink |
    |---------|------|---------|
    | 0 | home | [Home](/t/123) |               --> OK: standalone page at Level 0    
    | 1 | tutorial | [Tutorial](/t/124) |       --> OK: top-level parent folder at Level 1   
    | 2 | get-started | [Get started](/t/125) | --> OK: nested under a Level 1 parent   
    | 1 | some-other-page | [Some other page](/t/129) | --> OK: standalone page at Level 1
```
Example of a non-valid navigation structure:
```
    | 0 | tutorial | [Tutorial](/t/124) |       --> NOT OK: parent folder at Level 0  
    | 1 | get-started | [Get started](/t/125) | --> NOT OK: nested under a Level 0 parent   
```

**Requirement**: (mandatory) Pages should not be nested more than one level below the previous.
Example of a correct Level sequence:
```
    | 1 | <path> | [<title>](/t/<id>) |
    | 2 | <path> | [<title>](/t/<id>) |
    | 3 | <path> | [<title>](/t/<id>) |
    | 1 | <path> | [<title>](/t/<id>) | # skipping levels outwards is ok
```
Example of an incorrect Level sequence:
```
    | 1 | <path> | [<title>](/t/<id>) |
    | 3 | <path> | [<title>](/t/<id>) | # cannot skip levels inwards
```

> [!NOTE]
> Topics with a Navlink that is empty or points to an external link will simply be ignored. The following example Navlinks will be correctly processed:
> * `[Title](/t/123)` 
> * `[Title](/t/some-slug/123)`
> * `Title`
> * `[Title](http://discourse.instance.com/t/123)`
> * `[Title](http://discourse.instance.com/some-slug/123)`

#### Other requirements
**Requirement**: (mandatory) The docset should be consistent with **H1 headings**: either all pages have them, or none.

### Polish or troubleshoot your new Sphinx docs

Once you've run the script and built the HTML docs, you'll probably notice a few things that still need some polishing - maybe some formatting is off or the navigation doesn't show up as expected.

Here's a checklist of things to look out for:
* `conf.py`: 
  * **Important**: For myst cross-references to work, you must add the line `myst_heading_anchors = 4`. 
  * Edit the product title, links, and any other relevant settings.
* `index.md` pages: You may want to edit the `toctree`s to reflect a different order, display other titles, or remove unnecessary inclusions
* All `.md` pages: Check the formatting, since there might be some discourse-flavored markdown (e.g. stuff in `[square brackets][/square brackets]`) left over. More automatic substitutions are planned.
* Check the warnings in the output of the `make run` for common issues like links and cross-references that did not process correctly (see next section about [cross-references](#cross-references-and-links)), files that were not found by the auto-generated `toctree`, or code block syntax highlighting tags that aren't valid in Sphinx. (e.g. 'plain').

#### Cross-references and links
You will likely get several Sphinx build errors related to myst cross-reference targets. This is expected! There will be a few links that need to be fixed manually.

Here are some of the link-related warnings and fixes:

**Mismatched anchor**
```shell
WARNING: 'myst' cross-reference target not found: 'normal-looking-anchor'
```
Reason: This is probably because that anchor used to reference a manually created HTML heading. This means that it used to be `#heading--normal-looking-anchor`. The script automatically [replaces HTML headings with markdown ones](https://github.com/s-makin/discourse-offline-helper/pull/30), and removes the `heading--` prefix from the links. But the anchor you're left with may still not be a direct match with the heading name.

Fix: Manually replace that link with an anchor that corresponds to the actual name of the heading. See [this internal document](https://docs.google.com/document/d/1g56unMuhh5RcgfYew2c3AEClaBjYD9L5toF5xn3F5WY/edit?tab=t.0#heading=h.evr6ovkd4cbp) for more help finguring out the right heading anchor.

Another option is to create a custom MyST anchor associated to that heading: 
```
(my-custom-myst-anchor)=
## Some section
```
This would be referenced in any page as `See [some section](#my-custom-myst-anchor)`

**Invalid topic ID**
```shell
WARNING: 'myst' cross-reference target not found: ''
WARNING: 'myst' cross-reference target not found: '/'
```
Reason: The Discourse link (`/t/123`) references a page that is not in that documentation set's navtable, so the script doesn't know about it.

Fix: If this page is NOT part of your documentation set, manually replace the reference in the Sphinx doc with the full URL (`https://discourse.../t/123`).

If this page IS part of your documentation set but is not included in the navigation table, then you must either include it there or use a custom navtable (see the [argument descriptions](try-it-on-other-docs)) so that when you re-run the tool, the page is downloaded and all references to it are correctly replaced.

## Contribute

`discourse-offline-helper` is still in its early stages, so there's plenty of bugs to find, tests to write, and features to add.

Don't hesitate to raise an [issue on GitHub](https://github.com/s-makin/discourse-offline-helper/issues) or submit a PR! See [CONTRIBUTING.MD](CONTRIBUTING.md) for general contribution guidelines and suggestions. 

To get help or give feedback, please feel free to reach out to `@avgomes` on Mattermost. 
