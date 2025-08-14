# How it works

The Platform CLI is largely a wrapper around
[Copier](https://copier.readthedocs.io/en/stable/), with a few tweaks to support
easier-to-reason-about file exclusions and answers files in the
`.<TEMPLATE_NAME>/` subdirectories.

Review [Copier's basic
concepts](https://copier.readthedocs.io/en/stable/#basic-concepts) and [how
updates
work](https://copier.readthedocs.io/en/stable/updating/#how-the-update-works).

But in brief, when you install a template `template-foo` for app `bar` a few
things happen:

1. The repository for `template-foo` is cloned to a local temporary directory.
   - Note, the latest tagged version in the repository is checked out by
     default. Overridable with the `--version` arg.
1. The `copier.yml` file is read from the local `template-foo` clone, which
   provides the configuration and parameters of the template (e.g., what
   questions to ask the user).
1. If there are template parameters that need answered (and they have not been
   provided explicitly via `--data` args), the user is prompted for them.
1. A `.template-foo` directory is created at the top-level of the project with a
   `bar.yml` inside it, containing the version of the template used and the
   answers to the parameters for the `bar` instance of the template.
1. The files in the local clone of `template-foo` are iterated over and copied
   to the project, with templates being populated with the provided answers.

On update:

1. The repository for `template-foo` is cloned to a local temporary directory.
1. The version of `template-foo` currently used by the project is used to create
   a create a fresh instance of the template with the current project
   parameters, effectively a clean copy of the existing project as if it had
   just been created from the template.
1. This clean copy of the project is then compared to the actual current
   project, and the diff recorded. Effectively capturing any changes that have
   be made to the project outside of the template process itself, to re-apply
   later.
1. The latest tagged version (or value specified by `--version`) of
   `template-foo` is then applied to the project, prompting for any new
   parameters that need answers. Similar to the install process, though with
   some special logic around deleted files, etc.
1. `.template-foo/bar.yml` file at the top-level of the project is updated for
   the answers to any new parameters and the updated template version.
1. The diff of manual changes from before is applied.
