from pathlib import Path

from nava.infra_template import InfraTemplate
from nava.project import Project


def update(template_dir: str, project_dir: str, version: str | None = None) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update(project, version=version)


def update_base(template_dir: str, project_dir: str, version: str | None = None) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update_base(project, version=version)


def update_app(
    template_dir: str, project_dir: str, app_name: str, version: str | None = None
) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update_app(project, app_name, version=version)
