
## test_parse_navtable()
simple_case = \
"""[details=Navigation]

| Level | Path | Navlink |
|-------|------|---------|
| 1 | slug-a | [Page A](/t/123) |
| 2 | slug-b | [Page B](/t/124) |

[/details]"""

simple_case_result = \
    [{'Level': '1', 'Path': 'slug-a', 'Navlink': '[Page A](/t/123)'},
    {'Level': '2', 'Path': 'slug-b', 'Navlink': '[Page B](/t/124)'}]

markdown_variations = \
"""[details=Navigation]

| Level       | Path | Navlink |
|-----------|:------:|---------|
| 1 | slug-a | [Page A](/t/123) 
| 2 | slug-b | [Page B](/t/124) |

[/details]"""

markdown_variations_result = \
    [{'Level': '1', 'Path': 'slug-a', 'Navlink': '[Page A](/t/123)'},
    {'Level': '2', 'Path': 'slug-b', 'Navlink': '[Page B](/t/124)'}]

different_link_types = \
"""[details=Navigation]

| Level | Path | Navlink |
|-------|------|---------|
| 1 | slug-a | [Empty nav item]() |
| 2 | slug-b | [Local discourse page](/t/10592) |
| 3 | slug-c | [Local discourse page with slug](/t/some-text-in-between/10592) |
| 3 | slug-d | [Discourse page with partial URL](https://instance.discourse.io/t/10592) |
| 3 | slug-e | [Discourse page with full URL](https://instance.discourse.io/t/some-text-in-between/10592) |
| 2 | slug-f | [External link](https://somewhere-else.com) |

[/details]"""

different_link_types_result = \
    [{'Level': '1', 'Path': 'slug-a', 'Navlink': '[Empty nav item]()'},
    {'Level': '2', 'Path': 'slug-b', 'Navlink': '[Local discourse page](/t/10592)'},
    {'Level': '3', 'Path': 'slug-c', 'Navlink': '[Local discourse page with slug](/t/some-text-in-between/10592)'},
    {'Level': '3', 'Path': 'slug-d', 'Navlink': '[Discourse page with partial URL](https://instance.discourse.io/t/10592)'},
    {'Level': '3', 'Path': 'slug-e', 'Navlink': '[Discourse page with full URL](https://instance.discourse.io/t/some-text-in-between/10592)'},
    {'Level': '2', 'Path': 'slug-f', 'Navlink': '[External link](https://somewhere-else.com)'}]

## test_generate_filepaths()
navtable_diataxis_1_home_0 = \
"""[details=Navigation]

| Level | Path | Navlink |
|-------|------|---------|
| 0 | Home | [Home](/t/9729)
| 1 | tutorial | [Tutorial](/t/9722) |
| 2 | t-set-up | [1. Set up the environment](/t/9724) |
| 1 | how-to | [How To]() |
| 2 | h-deploy | [Deploy]() |
| 3 | h-deploy-lxd | [Deploy on LXD](/t/14575) |
| 2 | h-tls| [TLS encryption](/t/14783) |
| 3 | h-rotate-tls-ca-certificates   | [Rotate TLS/CA certificates](/t/15422) |
[/details]"""

navtable_diataxis_0 = \
"""[details=Navigation]

| Level | Path | Navlink |
|-------|------|---------|
| 0 | tutorial | [Tutorial](/t/9722) |
| 1 | t-set-up | [1. Set up the environment](/t/9724) |
| 0 | how-to | [How To]() |
| 1 | h-deploy | [Deploy]() |
| 2 | h-deploy-lxd | [Deploy on LXD](/t/14575) |
| 1 | h-tls| [TLS encryption](/t/14783) |
| 2 | h-rotate-tls-ca-certificates   | [Rotate TLS/CA certificates](/t/15422) |
[/details]"""

## test_generate_index_pages()
navtable_mixed_landing_pages = \
"""[details=Navigation]

| Level | Path | Navlink |
|-------|------|---------|
| 1 | tutorial | [Tutorial](/t/9722) |
| 2 | t-set-up | [1. Set up the environment](/t/9724) |
| 1 | how-to | [How To]() |
| 2 | h-deploy | [Deploy]() |
| 3 | h-deploy-lxd | [Deploy on LXD](/t/14575) |
| 2 | h-tls| [TLS encryption](/t/14783) |
| 3 | h-rotate-tls-ca-certificates   | [Rotate TLS/CA certificates](/t/15422) |
| 1 | test | |
|  | test2 | |
[/details]"""
