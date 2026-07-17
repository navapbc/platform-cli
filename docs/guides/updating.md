# Updating a project

A key value for utilizing the Strata templates is not only getting off the
ground, but staying up to date with new features and developments that are
provided in the upstream templates.

The CLI is designed to try to make that process of keeping up to date easier.
You can help yourself further by following the [guide on avoiding conflicts on
update](./avoiding-conflicts-on-update.md).


!!! info

    You can not update a project repo that is "dirty" (i.e., has untracked files
    or pending changes according to Git).

    So for template updates, it can be useful to have a dedicated
    [worktree](https://git-scm.com/docs/git-worktree) separate from your main
    development one (or stash changes, maintain an entirely separate local
    "clean" repo, etc.).

!!! note

    Reminder, the template commands will assume you want to update to the latest
    released version of the relevant template. If that is not what you, specify
    `--version <your target>` on the update commands.

## Infra templates

```sh
nava-platform infra update .
```

This will attempt to update the "base" template then each "app" instance in
sequence. This can often run into merge conflicts that need resolved manually.
The tool will provide some guidance if this happens.

But you can also approach the update in the separate pieces yourself, first
updating the infrastructure base with:

```sh
nava-platform infra update-base .
```

Then all the infrastructure for each application with:

```sh
nava-platform infra update-app --all .
```

(drop `--all` if you would rather choose the order to update the applications)

## Application templates

```sh
nava-platform app update . <APP_NAME>
```
