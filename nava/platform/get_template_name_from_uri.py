from pathlib import Path


def get_template_name_from_uri(template_uri: Path | str) -> str:
    # generally the template name should be the last part of the
    # template URI
    return Path(template_uri).name.removesuffix(".git")
