# Using the CLI

After [installing the CLI](./installation.md), verify it is, in fact, installed
and check out the main help page by running:

``` sh
nava-platform --help
```

This will show you available commands and some more information. You can check
out [the guides](../guides/index.md) for detailed instructions for various uses
of the CLI.

But, the main functionality of the CLI is to support using the Strata templates
and you are likely wanting to start there.

## Strata templates

!!! info

    The template commands will use the **latest released version** of a template
    unless otherwise specified with the `--version` flag. For general usage it's
    recommended to stick to released versions, but for example you can use
    `--version HEAD` to get latest (unreleased) template content.

### Entire project (infra + apps)

!!! note

    You should have an cloud (AWS/Azure) account provisioned with admin access
    before starting.

If you are looking to stand up a cloud environment, see [the guide on starting a
new project](../guides/new-project.md).

The Strata infrastructure templates really require a concrete environment to do
anything useful, so you can try out generating project code with them, but not
much more without a cloud environment to run against.

### Local app

If you just want to test things out locally, you probably want one of the
[Strata application
templates](https://github.com/navapbc/strata#strata-application-templates),
which have their install commands in their READMEs. For the general process or
if you have an existing project that you would like to add an app to, see the
[guide on adding an application](../guides/adding-an-app.md).

### Legacy template versions

For projects using the legacy install/update scripts, see [the guide on
migrating to the CLI](../guides/migrating-from-legacy-template.md).
