from pathlib import Path

from nava.infra_template import InfraTemplate
from nava.project import Project
from .compute_app_includes_excludes import compute_app_includes_excludes
from .get_app_names import get_app_names


def update(template_dir: str, project_dir: str):
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update(project)
