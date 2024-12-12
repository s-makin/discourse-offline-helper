# CONTRIBUTING

The general logic (`main.py`) is split into two parts:
1. Downloading Discourse docs locally (via the `DiscourseHandler` class)
2. Processing the contents to render correctly with Sphinx/RTD (via the `SphinxHandler` class)

While a lot of the logic could be combined for optimization, this structure was implemented so that it's straightforward to test and modify the code in cases like:
* a particular documentation set needs to be processed in a slightly different way in a particular step
* new features are introduced
* easy handling of optional features - if a user only wants to run a particular set of steps, e.g. download Discourse pages locally without changing the markdown, they can create a new main method with the steps they want to run
* a platform other than Discourse or Sphinx can be easily introduced without re-implementing all of functionality

With this general principle of modularity and reusability in mind, contributors are more than welcome to improve the current architecture, specific features, or tests.

(WIP)