import re
from contextlib import AbstractContextManager, nullcontext

from packaging.version import Version

from nava.platform.projects.migrate_from_legacy_template import MIGRATION_TAG_PREFIX
from nava.platform.util.git import GitProject


def get_template_git(template_uri: str | None) -> AbstractContextManager[GitProject | None]:
    if template_uri:
        template_git_ctx: AbstractContextManager[GitProject | None] = GitProject.clone_if_necessary(
            template_uri
        )
    else:
        template_git_ctx = nullcontext(None)

    return template_git_ctx


def get_releases(template_git: GitProject) -> list[Version]:
    template_tagged_versions = template_git.get_tags("--list", "v*")
    return sorted(map(Version, template_tagged_versions))


def get_newer_releases(
    current_version: str,
    template_git: GitProject | None = None,
    template_versions: list[Version] | None = None,
) -> list[Version] | None:
    if template_versions is not None:
        versions_to_compare = template_versions
    elif template_git is not None:
        versions_to_compare = get_releases(template_git)
    else:
        return None

    project_v = get_version(current_version.removeprefix(MIGRATION_TAG_PREFIX))
    if not project_v:
        return None

    return list(filter(project_v.__le__, versions_to_compare))


# derived from https://github.com/copier-org/copier/blob/63fec9a500d9319f332b489b6d918ecb2e0598e3/copier/template.py#L575
def get_version(v: str) -> Version | None:
    try:
        return Version(v)
    except ValueError:
        if re.match(r"^.+-\d+-g\w+$", v):
            base, count, git_hash = v.rsplit("-", 2)
            return Version(f"{base}.post{count}+{git_hash}")

    return None
