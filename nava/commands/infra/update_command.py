from pathlib import Path

from nava.infra_template import InfraTemplate
from nava.project import Project


def update(template_dir: str, project_dir: str, version: str | None = None):
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update(project, version=version)
