from pathlib import Path

from nava.infra_template import InfraTemplate
from nava.project import Project


def migrate_from_legacy(project_dir: str, origin_template_uri: str) -> None:
    project = Project(Path(project_dir))
    project.migrate_from_legacy(origin_template_uri)

