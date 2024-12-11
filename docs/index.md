
# Charmed OpenSearch Documentation
Charmed OpenSearch is an open-source software operator that packages the [OpenSearch](http://opensearch.org/) search and data analytics suite with simplified deployment, operation, and management via the Juju CLI. It can be deployed on physical and virtual machines, as well as other cloud and cloud-like environments, including AWS, Azure, OpenStack and VMWare. 

Charmed OpenSearch  has multiple operator features such as automated deployment, TLS encryption, user management, horizontal scaling, replication, password rotation, and easy integration with other applications. 

This charm is for anyone looking for a complete data analytics suite. You could be a team of system administrators maintaining large data infrastructures, a software developer who wants to connect their application with a powerful search engine, or even someone curious to learn more about Charmed OpenSearch through our guided tutorial.

To see the Charmed OpenSearch features and releases, visit our [GitHub Releases page](https://github.com/canonical/opensearch-operator/releases).
<!--
The Charmed OpenSearch (VM Operator) release aligns with the [OpenSearch upstream major version naming](https://opensearch.org/docs/latest/version-history/). OpenSearch releases major versions such as 1.0, 2.0, and so on.

A charm version combines both the application major version and / (slash) the channel, e.g. `2/stable`, `2/candidate`, `2/edge`. 
The channels are ordered from the most stable to the least stable, candidate, and edge. More risky channels like edge are always implicitly available. 
So, if the candidate is listed, you can pull the candidate and edge. When stable is listed, all three are available.

The upper portion of this page describes the Operating System (OS) where the charm can run, e.g. 2/stable is compatible and should run on a machine with Ubuntu 22.04 OS.
-->

## In this documentation
| | |
|--|--|
|  [**Tutorials**](/tutorial/tutorial)</br>  [Get started](/tutorial/tutorial) - a hands-on introduction to using the Charmed OpenSearch operator for new users </br> |  [**How-to guides**](/how-to/scale-horizontally) </br> Step-by-step guides covering key operations such as [scaling](/how-to/scale-horizontally), [TLS encryption](/how-to/tls-encryption/enable-tls-encryption), or [monitoring](/how-to/enable-monitoring) |
| [**Reference**](/reference/charm-testing) </br> Technical information such as [system requirements](/reference/system-requirements) | <!--[Explanation]() </br> Concepts - discussion and clarification of key topics-->  |

## Project & community
Charmed OpenSearch is an official distribution of OpenSearch . It’s an open-source project that welcomes community contributions, suggestions, fixes and constructive feedback.
- Raise an issue or feature request in the [Github repository](https://github.com/canonical/opensearch-operator/issues).
- Meet the community and chat with us in our [Matrix channel](https://matrix.to/#/#charmhub-data-platform:ubuntu.com) or [leave a comment](https://discourse.charmhub.io/t/charmed-opensearch-documentation/9729).
- See the Charmed OpenSearch [contribution guidelines](https://github.com/canonical/opensearch-operator/blob/main/CONTRIBUTING.md) on GitHub and read the Ubuntu Community's [Code of Conduct](https://ubuntu.com/community/code-of-conduct).

## License & trademark
The Charmed OpenSearch ROCK, Charmed OpenSearch Snap, and Charmed OpenSearch Operator are free software, distributed under the 
[Apache Software License, version 2.0](https://github.com/canonical/charmed-opensearch-rock/blob/main/licenses/LICENSE-rock). They install and operate OpenSearch, 
which is also licensed under the [Apache Software License, version 2.0](https://github.com/canonical/charmed-opensearch-rock/blob/main/licenses/LICENSE-opensearch).

OpenSearch is a registered trademark of Amazon Web Services. Other trademarks are property of their respective owners. Charmed OpenSearch is not sponsored, 
endorsed, or affiliated with Amazon Web Services.

This documentation follows the [Diataxis Framework](https://canonical.com/blog/diataxis-a-new-foundation-for-canonical-documentation).

## Navigation

[details=Navigation]

| Level | Path                       | Navlink                                      |
|----------|-------------------------|----------------------------------------------|
| 1 | tutorial | [Tutorial](/tutorial/tutorial)                                 |
| 2 | t-set-up | [1. Set up the environment](/tutorial/1-set-up-the-environment) |
| 2 | t-deploy-opensearch | [2. Deploy OpenSearch](/tutorial/2-deploy-opensearch) |
| 2 | t-enable-tls | [3. Enable encryption](/tutorial/3-enable-encryption) |
| 2 | t-integrate | [4. Integrate with a client application](/tutorial/4-integrate-with-a-client-application) |
| 2 | t-passwords | [5. Manage passwords](/tutorial/5-manage-passwords) |
| 2 | t-horizontal-scaling | [6. Scale horizontally](/tutorial/6-scale-horizontally)  |
| 2 | t-clean-up | [7. Clean up the environment](/tutorial/7-clean-up-the-environment) |
| 1 | how-to | [How To]() |
| 2 | h-deploy | [Deploy]() |
| 3 | h-deploy-lxd | [Deploy on LXD](/how-to/deploy/deploy-on-lxd) |
| 3 | h-large-deployment | [Launch a large deployment](/how-to/deploy/launch-a-large-deployment) |
| 2 | h-tls| [TLS encryption]() |
| 3 | h-enable-tls | [Enable TLS encryption](/how-to/tls-encryption/enable-tls-encryption) |
| 3 | h-rotate-tls-ca-certificates   | [Rotate TLS/CA certificates](/how-to/tls-encryption/rotate-tls-ca-certificates) |
| 2 | h-horizontal-scaling  | [Scale horizontally](/how-to/scale-horizontally) |
| 2 | h-integrate | [Integrate with an application](/how-to/integrate-with-an-application) |
| 2 | h-backups | [Back up and restore]() |
| 3 | h-configure-s3 | [Configure S3](/how-to/back-up-and-restore/configure-s3) |
| 3 | h-create-backup | [Create a backup](/how-to/back-up-and-restore/create-a-backup) |
| 3 | h-restore-backup | [Restore a local backup](/how-to/back-up-and-restore/restore-a-local-backup) |
| 3 | h-migrate-cluster | [Migrate a cluster](/how-to/back-up-and-restore/migrate-a-cluster) |
| 2 | h-upgrade | [Upgrade]() |
| 3 | h-minor-upgrade | [Perform a minor upgrade](/how-to/upgrade/perform-a-minor-upgrade) |
| 3 | h-minor-rollback | [Perform a minor rollback](/how-to/upgrade/perform-a-minor-rollback) |
| 2 | h-load-testing | [Perform load testing](/how-to/perform-load-testing) |
| 2 | h-attached-storage| [Recover from attached storage](/how-to/recover-from-attached-storage) |
| 2 | h-enable-monitoring | [Enable monitoring](/how-to/enable-monitoring) |
| 1 | reference | [Reference]() |
| 2 | release-notes| [Release notes]() |
| 3 | revision-168| [Revision 168](/reference/release-notes/revision-168) |
| 2 | r-system-requirements | [System requirements](/reference/system-requirements) |
| 2 | r-software-testing | [Charm testing](/reference/charm-testing) |

[/details]


```{toctree}
:hidden:
:titlesonly:
:maxdepth: 2
:glob:

self
/tutorial/index
/how-to/index
/reference/index
/explanation/index
