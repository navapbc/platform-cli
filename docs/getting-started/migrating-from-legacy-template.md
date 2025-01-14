# Migrating old templates to Nava Platform CLI

Previously templates would (generally) store the version installed into a
`.<TEMPLATE_NAME>-version` file at the root of the project. Templates updated to
use the Platform CLI track this info in a different way, so before utilizing the
Platform CLI you'll need to convert the old file into the new format.

The Platform CLI provides commands for doing this migration, though the exact
steps you need to take will vary depending on what templates you have installed.

> [!IMPORTANT]
>
> If you running a very old (pre-summer 2024) version of a template
> (particularly `template-infra`), reach out to the platform team for some
> guidance.

## template-infra

To transform the old `.template-version` file into the new format, run:

```sh
nava-platform infra migrate-from-legacy --commit .
```

This will result in a `.template-infra/` directory with a number of files inside
of it. Check that the `app-<APP_NAME>.yml` files all coorespond to proper
applications. Remove any that don't and update the commit.


Now perform the update, with:

```sh
nava-platform infra update .
```

This will attempt to update the "base" template then each "app" instance in
sequence. This will likely bail after updating the base infra template files,
with a message to fix merge conflicts manually and run the update in parts. So
fix the merge conflicts and commit.

Then pickup the update from where it left off:

```sh
nava-platform infra update-app --all .
```

Likely you'll hit merge conflicts for each app as well, resolve those, commit,
and move on to the next app, until you've done them all.

## Application templates

These are historically less standard, so you'll have to provide a little more
info, see `nava-platform app migrate-from-legacy --help`.

```sh
nava-platform app migrate-from-legacy --origin-template-uri <TEMPLATE_URI> --legacy-version-file <OLD_VERSION_FILE> . <APP_NAME>
```

The `<OLD_VERSION_FILE>` will likely be one of:

- `.template-flask-version`
- `.template-nextjs-version`
- `.template-application-rails-version`

but your project may have renamed it.

You can then run:

```sh
nava-platform app update . <APP_NAME>
```

> [!IMPORTANT]
> Review the changes, you may need to restore some project root files like:
>
> - `README.md`
> - `.github/pull_request_template.md`
>
> This is due to how the underlying update runs and the initial migration to the
> updated templates. Should not be an issue once running an updated template.
>
> Restore the version from the current remote `main` branch with something like:
>
> ```sh
> git checkout origin/main -- README.md .github/pull_request_template.md
> ```

### template-application-flask

After doing the migrate+initial update, you may want to restore `.dockleconfig`
and `.hadolint.yaml` from template-infra:

```sh
curl -O https://raw.githubusercontent.com/navapbc/template-infra/refs/heads/main/.dockleconfig
curl -O https://raw.githubusercontent.com/navapbc/template-infra/refs/heads/main/.hadolint.yaml
```

### template-application-nextjs

After doing the migrate+initial update, you may want to restore `.grype.yml`
from template-infra:

```sh
curl -O https://raw.githubusercontent.com/navapbc/template-infra/refs/heads/main/.grype.yml
```
