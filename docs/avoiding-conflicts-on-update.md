# Avoiding conflicts on update

At the moment the "Nava Platform" is effectively just some structure around
copying source files. This provides a lot of flexibility for projects to
customize things to their needs, see exactly the code that changes between
versions, and other benefits, but also introduces higher chances of merge
conflicts on updating from upstream. There's logic in the Platform CLI to
automatically resolve some of these, and thankfully Git can help tease things
apart where we can't automatically resolve the conflicts, but you can also take
steps to avoid some conflicts in the first place, as template maintainers and
template users.

> [!TIP]
>
> As is often the case, it is easier to resolve conflicts in smaller chucks.
> Frequently updating from upstream can help avoid the worst situations.

## Upstream in templates

See [Template technical design
principles](https://github.com/navapbc/template-infra/blob/main/template-only-docs/template-technical-design-principles.md)
for general guidance.

When possible, prefer to isolate template-owned files/configuration in separate
files that can be imported into the proper runtime location. Provides users a
way layer customization on top without having to edit files that might get
touched on update.

## Downstream template users

### template-infra

You may want to avoid creating `/infra/modules/` directories with very generic
names. As upstream may eventually ship generic functionality (or a generic
interface) for that use case, creating a situation where you may be blocked on
updating until resolving all the conflicts. For example, for a non-upstream
version of "notifications" for `<PROJECT_NAME>`, consider calling the module
`<PROJECT_NAME>_notifications/` rather than `notifications/`.

### Application templates

Application templates tend to touch files that projects also customize heavily
(e.g. `README.md`, CI workflow files, root-level config files), so conflicts are
more likely here than in infra templates. A few practical strategies:

**Know which files are template-owned.** Run `git log --follow <file>` on files
you intend to customize to see whether they were originally written by the
template. If so, expect that upstream may update them and plan accordingly.

**Use thin wrapper files where possible.** If an application template ships a
CI workflow you need to tweak, prefer adding a separate workflow file that
extends or supplements it rather than editing the template-owned file directly.
The same applies to configuration files that support an "include" or "extend"
mechanism (e.g. ESLint, TypeScript, Prettier configs).

**Isolate project-specific content.** Files like `README.md` and
`.github/pull_request_template.md` are natural conflict points. Consider keeping
project-specific content in a separate included file (e.g.
`docs/project-overview.md`) and keeping the template-owned file minimal.

**Commit project customizations separately from template updates.** When you
first apply a template, make one commit for the raw template output and a
follow-up commit for your project-specific edits. This makes future 3-way merges
cleaner because the "yours" side is clearly separated.

**Update frequently.** Smaller, more frequent updates mean each merge has less
divergence to reconcile. Letting many template versions accumulate makes
conflicts significantly harder to untangle.
