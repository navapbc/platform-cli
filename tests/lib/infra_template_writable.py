from pathlib import Path
from typing import Any

from nava.platform.cli.context import CliContext
from nava.platform.infra_template import InfraTemplate
from nava.platform.util.git import GitProject


class InfraTemplateWritable:
    """Manipulate the template's files."""

    ctx: CliContext
    template_dir: Path
    git_project: GitProject
    ref: str | None

    def __init__(self, ctx: CliContext, template_dir: Path, ref: str | None = None) -> None:
        self.ctx = ctx
        self.template_dir = template_dir
        self.git_project = GitProject(template_dir)
        self.ref = ref

    @property
    def template(self) -> InfraTemplate:
        # a little hacky to return a new instance every time, but will help
        # pickup any underlying changes to the git repo, though callers will
        # need to set `ref` manually if running things against a particular
        # version for things to be right
        return InfraTemplate(self.ctx, self.template_dir, ref=self.ref)

    def __getattr__(self, attr: str) -> Any:
        return getattr(self.template, attr)
