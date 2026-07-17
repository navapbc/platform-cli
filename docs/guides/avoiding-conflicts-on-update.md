# Using templates while avoiding conflicts on update

The Strata templates workflow is effectively just some structure around copying
source files. This provides a lot of flexibility for projects to customize
things to their needs, see exactly the code that changes between versions, and
other benefits, but also introduces higher chances of merge conflicts on
updating from upstream. There's logic in the CLI to automatically resolve some
of these, and thankfully Git can help tease things apart where we can't
automatically resolve the conflicts, but you can also take steps to avoid some
conflicts in the first place, as template maintainers and template users.

!!! tip "Update frequently"

    As is often the case, it is easier to resolve conflicts in smaller chucks.
    Frequently updating from upstream can help avoid the worst situations.

## Upstream in templates

Template maintainers should follow the [template technical design
principles][template-design] for general guidance.

[template-design]: https://github.com/navapbc/template-infra/blob/main/template-only-docs/template-technical-design-principles.md

When possible, prefer to isolate template-owned files/configuration in separate
files that can be imported into the proper runtime location. Provides users a
way layer customization on top without having to edit files that might get
touched on update.

## Downstream template users

### Infra templates

You may want to avoid creating `/infra/modules/` directories with very generic
names. As upstream may eventually ship generic functionality (or a generic
interface) for that use case, creating a situation where you may be blocked on
updating until resolving all the conflicts. For example, for a non-upstream
version of "notifications" for `<PROJECT_NAME>`, consider calling the module
`<PROJECT_NAME>_notifications/` rather than `notifications/`.

### Application templates

No good advice at the moment. It can be hard to avoid conflicts given the nature
of applications. But at least keep in mind which files are tracked upstream.
