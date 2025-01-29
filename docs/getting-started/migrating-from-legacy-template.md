# Migrating old templates to Nava Platform CLI

Previously templates would (generally) store the version installed into a
`.<TEMPLATE_NAME>-version` file at the root of the project. Templates updated to
use the Platform CLI track this info in a different way, so before utilizing the
Platform CLI you'll need to convert the old file into the new format.

The Platform CLI provides commands for doing this migration, though the exact
steps you need to take will vary depending on what templates you have installed.

## template-infra

The switch to Platform CLI happened with `v0.15.0`. If you are running a version
earlier than this, you'll need to migrate things.

One way to figure out what version of `template-infra` your project is using is
to run, at the root of your project:

```sh
nava-platform infra info --template-uri gh:navapbc/template-infra .
```

Look for the "Closest upstream version" value. If it is "Unknown", reach out to
the Platform team for guidance.

If the value is pre-`v0.12.0`, you may want to approach the update in smaller
steps than jumping directly to `v0.15.0`. You can use the Platform CLI to do
these updates as well, see [Migrate in smaller
steps](#migrate-in-smaller-steps).

As always, read the [release
notes](https://github.com/navapbc/template-infra/releases) for each version
between your current one and your ultimate target. This process does not
eliminate the need to apply the state changes/manual migration steps, it just
updates the code. See [Version callouts](#version-callouts) below for some
particular things to consider.

### Migrate to latest

To transform the old `.template-version` file into the new format, run:

```sh
nava-platform infra migrate-from-legacy --commit .
```

This will result in a `.template-infra/` directory with a number of files inside
of it. Check that the `app-<APP_NAME>.yml` files all correspond to proper
applications. Remove any that don't and update the commit.

This gets your project into a state that Platform CLI can understand.

Now perform the actual template update, with:

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

See [the docs on updating in general](../updating.md) for more details on running
updates.

### Migrate in smaller steps

This is similar to the previous section, so read that first.

1. Run the `migrate-from-legacy` command as stated in previous section. This
   gets you into the Platform CLI ecosystem.
2. Then decide which version of `template-infra` you want to update to,
   represented by `v0.x.x` in the following example:
   ```sh
   nava-platform infra update --version platform-cli-migration/v0.x.x .
   ```
3. Follow update guidance as discussed in previous section.
4. Do steps 2-3 over and over, jumping versions as you see fit until you hit
   `v0.15.0`.
5. Once on `v0.15.0`, run a final update to get to the latest release (or to
   whatever post-`v0.15.0` version you want):
   ```sh
   nava-platform infra update [--version vA.B.C] .
   ```

### Version callouts

No substitute for reading the [release
notes](https://github.com/navapbc/template-infra/releases), but here are a few
points to consider when deciding what version to update to if you are
significantly behind the latest:

- A Feature Flags module, backed by AWS Evidently, was added in
  [v0.5.0](https://github.com/navapbc/template-infra/releases/tag/v0.5.0) and
  removed in
  [v0.13.0](https://github.com/navapbc/template-infra/releases/tag/v0.13.0).
    - If you are coming from pre-v0.5.0, you can delete the feature flag module
      as you move past v0.5.0, or just ignore/don't change anything about it and
      it will get cleaned up once you are post-v0.13.0.
- [v0.9.0](https://github.com/navapbc/template-infra/releases/tag/v0.9.0) moved
  account mapping to each environment config file, then
  [v0.11.0](https://github.com/navapbc/template-infra/releases/tag/v0.11.0)
  removed it from each environment config file and moved it to the network config.
    - If you are pre-v0.9.0, you may want to consider jumping to v0.11.x+ to
      avoid dealing with moving things multiple times.

Misc. others:

- [v0.11.0](https://github.com/navapbc/template-infra/releases/tag/v0.11.0)
    - Starts pinning specific Terraform version in CI/CD
- [v0.10.0](https://github.com/navapbc/template-infra/releases/tag/v0.10.0)
    - DB changes: PostgreSQL version update to 16.2 and DB schema name hardcoded
to `app`
- [v0.9.0](https://github.com/navapbc/template-infra/releases/tag/v0.9.0)
    - Requires Terraform 1.8.x (previous requirement was just >=1.4, more or less)
    - Changes the way secrets are defined
- [v0.7.0](https://github.com/navapbc/template-infra/releases/tag/v0.7.0)
    - Minor state migration needed
- [v0.6.0](https://github.com/navapbc/template-infra/releases/tag/v0.6.0)
    - Networking changes likely requiring hours of downtime to apply

### Post-migration

After completing the migration, you may want to see what results from
re-applying, more holistically, the latest (or your ultimate target) version of
the template to the project:

```sh
nava-platform infra update --force [--version vA.B.C] .
```

This discards some of the "smart" logic of a regular update and might catch some
things that were missed while trying to be smarter.

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

## Brute-force

The previous sections describe an approach that will try to do a smarter
migration, but if a) that is failing and b) you have some understanding of any
deviations of your project from the upstream templates, you also have the option
to force the new version of the template on your existing project:

```sh
nava-platform infra install .
```

You will be prompted to overwrite conflicting files, which you probably want to
do. There are likely files that have been moved in the new version, you'll have
to manually clean up the old ones. Then check the git diff, adjust the changes
as necessary. Then commit.

### Multiple applications

If you have multiple applications, you may want to force the install above for
only a single app to start by adding specifying `--data app_name=<APP_NAME>` on
the `infra install`.

Then the other apps one at a time, with:

```sh
nava-platform infra add-app . <APP_NAME>
```

Optionally, if you want to force an application-template version as well:

```sh
nava-platform app install . <APP_NAME>
```
