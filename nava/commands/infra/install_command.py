from pathlib import Path
import click


from nava.infra_template import InfraTemplate
from nava.project import Project
from .get_app_names import get_app_names
from . import add_app_command

from .compute_app_includes_excludes import (
    compute_app_includes_excludes,
)


def install(template_dir: str, project_dir: str):
    template = InfraTemplate(Path(template_dir))
    template.install(Project(Path(project_dir)))
