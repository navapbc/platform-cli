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

No good advice at the moment. It can be hard to avoid conflicts given the nature
of applications. But at least keep in mind which files are tracked upstream.
