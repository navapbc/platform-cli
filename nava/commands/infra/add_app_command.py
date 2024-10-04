from pathlib import Path

from nava.infra_template import InfraTemplate
from nava.project import Project


def add_app(template_dir: str | Path, project_dir: str, app_name: str) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.add_app(project, app_name)
