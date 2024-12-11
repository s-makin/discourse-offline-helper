
# Tutorial

This tutorial is designed to help you learn how to deploy Charmed OpenSearch and become familiar with its available operations.

>To get started right away, go to [**Step 1. Set up the environment**](/tutorial/1-set-up-the-environment).

## Prerequisites
While this tutorial intends to guide you as you deploy Charmed OpenSearch for the first time, it will be most beneficial if:

* You have some experience using a Linux-based CLI
* You are familiar with OpenSearch concepts such as indices and users.
  * To learn more, see the official [OpenSearch Documentation](https://opensearch.org/docs/latest/about/)
* Your computer fulfils the [minimum system requirements](/reference/system-requirements)

## Tutorial contents

The following topics are covered:

| Step | Details |
| ------- | ---------- |
| 1. [**Set up the environment**](/tutorial/1-set-up-the-environment) | Set up a cloud environment for you deployment with LXD |
| 2. [**Deploy OpenSearch**](/tutorial/2-deploy-opensearch) | Learn how to deploy OpenSearch with Juju |
| 3. [**Enable TLS encryption**](/tutorial/3-enable-encryption) | Enable security in your deployment by integrating with a TLS certificates operator
| 4. [**Integrate with a client application**](/tutorial/4-integrate-with-a-client-application) | Learn how to a client app with OpenSearch and manage users
| 5. [**Manage passwords**](/tutorial/5-manage-passwords) | Learn about password management and rotation
| 6. [**Scale horizontally**](/tutorial/6-scale-horizontally) | Scale your application by adding or removing juju units
| 7. [**Clean up the environment**](/tutorial/7-clean-up-the-environment) | Remove your OpenSearch deployment and juju to free your machine's resources

> **Get started**: [Step 1. Set up the environment](/tutorial/1-set-up-the-environment)


```{toctree}
:hidden:
:titlesonly:
:maxdepth: 2
:glob:

*
*/index
