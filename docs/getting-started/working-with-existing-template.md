# Working with an existing app template

This guide covers how to develop and test changes to an app template (e.g., `template-application-rails`, `template-application-flask`) and apply those changes to a project using the Platform CLI.

## How template versioning works

The Platform CLI uses [Copier](https://copier.readthedocs.io/en/stable/) under the hood, which relies on **Git tags** for version resolution. When you run an `install` or `update` command, the CLI clones the template repository and **checks out the latest tagged version** by default — not `main` or any other branch.

This means:

- **Tags are the source of truth.** The CLI will not pick up commits on `main` unless those commits are included in a tagged release.
- **A new tag must be created** in the template repository for the CLI to recognize and install new changes.
- Tags should follow [PEP 440](https://peps.python.org/pep-0440/) versioning (e.g., `v0.1.0`, `v0.2.0`). Non-compliant tags are ignored during version resolution.

> [!IMPORTANT]
> Simply merging changes to `main` in a template repository is **not sufficient** for those changes to be picked up by the CLI. A new version tag must be pushed to the repository.

### Example: releasing a new template version

After merging your changes to the template's `main` branch:

```sh
# In the template repository
git tag v0.3.0
git push origin v0.3.0
```

Projects can then pick up this version:

```sh
nava-platform app update . myapp
```

## Developing with a local template

When working on template changes, you don't need to push to a remote or create tags. The CLI supports pointing directly at a **local directory** and a specific **branch or ref**, which is ideal for development and testing.

### Setting up a local checkout

Clone the app template repository (or use an existing clone):

```sh
git clone https://github.com/navapbc/template-application-rails ~/templates/template-application-rails
```

Create a branch for your changes:

```sh
cd ~/templates/template-application-rails
git checkout -b my-feature-branch
```

Make your template changes and commit them.

> [!NOTE]
> Template changes must be committed to your local branch. Copier works from Git history, so uncommitted changes will not be applied.

### Using a Git worktree (alternative)

If you'd rather keep your default branch intact, you can use a [Git worktree](https://git-scm.com/docs/git-worktree) instead of a new clone:

```sh
cd ~/templates/template-application-rails
git worktree add ../template-application-rails-feature my-feature-branch
```

This creates a separate working directory at `../template-application-rails-feature` checked out to `my-feature-branch`, while leaving your original clone on its current branch.

### Installing from a local template

Use `--template-uri` to point to your local checkout, and `--version` to specify the branch:

```sh
nava-platform app install \
  --template-uri ~/templates/template-application-rails \
  --version my-feature-branch \
  --commit \
  . myapp
```

### Updating from a local template

Similarly, to update an existing project using your local template changes:

```sh
nava-platform app update \
  --template-uri ~/templates/template-application-rails \
  --version my-feature-branch \
  --commit \
  . myapp
```

> [!TIP]
> Use `--version HEAD` to always apply the latest commit on the default branch of your local checkout, regardless of tags.

### Key CLI options for local development

| Option | Description |
|---|---|
| `--template-uri` | Path or URL to the template source. Can be a local path (e.g., `~/templates/template-application-rails`) or a remote URL. |
| `--version` | Template version to use. Accepts a branch name, tag, commit hash, or `HEAD`. Defaults to the latest tag. |
| `--template-name` | Override the template name if your local directory has a different name than the upstream repository (e.g., if your worktree folder is named differently). |
| `--commit` | Automatically commit the generated changes with a standard message. |

## Infra template local development

The infra template works the same way. The default `--template-uri` for `infra` commands is `https://github.com/navapbc/template-infra`, but you can override it:

```sh
nava-platform infra install \
  --template-uri ~/templates/template-infra \
  --version my-feature-branch \
  --commit \
  . myapp
```

```sh
nava-platform infra update \
  --template-uri ~/templates/template-infra \
  --version my-feature-branch \
  .
```

## Summary

| Scenario | What to do |
|---|---|
| Use the latest released template version | Just run `install` or `update` — the CLI defaults to the latest tag. |
| Release a new template version for all projects | Tag a new version in the template repo and push it. |
| Test local template changes during development | Use `--template-uri` pointed at your local clone and `--version` set to your branch. |
| Always use the latest commit (skip tag resolution) | Pass `--version HEAD`. |
