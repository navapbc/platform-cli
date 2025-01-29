# Updating

A key value for utilizing the Nava Platform is not only getting off the ground,
but staying up to date with new features and developments that are provided in
the upstream templates.

The Platform CLI is designed to try to make that process of keeping up to date
easier. You can help yourself further by following the advice in [Avoiding
Conflicts on Update](./avoiding-conflicts-on-update.md).

> [!IMPORTANT]
>
>  You can not update a project repo that is "dirty" (i.e., has untracked files
>  or pending changes according to Git).
>
>  So for template updates, it can be useful to have a dedicated
>  [worktree](https://git-scm.com/docs/git-worktree) separate from your main
>  development one (or stash changes, maintain an entirely separate local
>  "clean" repo, etc.).

## template-infra

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
