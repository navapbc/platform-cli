from pathlib import Path
import copier

from nava.infra_template import InfraTemplate
from nava.project import Project

from .compute_app_includes_excludes import (
    compute_app_includes_excludes,
)


def add_app(template_dir: str | Path, project_dir: str, app_name: str):
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.add_app(project, app_name)
