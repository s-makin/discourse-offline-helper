# README

> [!NOTE]
> This is under active development and is not ready for general use.
> 
> If you are interested, please get in touch with Andreia Velasco (@a-velasco)!

The `doh` module:
* Downloads discourse documentation locally into markdown files, conserving the original navigation structure
* **(WIP)** Converts downloaded documentation into a Sphinx-compatible format

## demo
The following instructions will show you how to set up your environment and run the script. 

By default, it'll download a demo documentation set ([Charmed OpenSearch](https://charmhub.io/opensearch)) into a local `'/docs'` folder:

Clone the repo and enter its root directory:
```
git clone git@github.com:a-velasco/offline-helper.git
cd offline-helper
```

Start a virtual environment (called `demo` in the example below):
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
python3 doh/main.py
```
## configuration

To configure the inputs, open `main.py` and edit the input parameters on [line 24](doh/main.py#L24): `docset` and `docs_local_path`.

For example, to download MongoDB docs directly to my test sphinx repo, I set:
```
docset = mongodb
docs_local_path = '/home/andreia/Documents/pdf-test-repo/docs/'
```

>[!NOTE]
> Before re-running the script on a different docset, manually delete the pre-existing files.
>
> The script overwrites existing files when re-downloading them.
> This means that if you run it with a different docset to the same target folder, the previous docset's files will remain there and mix with the new.
