import dataclasses
from typing import ClassVar, NewType, Self, cast

TemplateId = NewType("TemplateId", str)


@dataclasses.dataclass(frozen=True)
class TemplateName:
    """Handling the "name" of "a" "template".

    There are a number of conventions the tooling follows based on the "name" of
    a template. Most of the time a single repo == a single template and the
    "name" of the template is just the name of the repo. Easy.

    Some times, notably ``navapbc/template-infra``, there are multiple
    "templates" (a distinct collection of templated files that are handled
    together) in the same repo, though the repo itself is also referred to as a
    "template" in conversation. These multiple templates are not necessarily
    hierarchical, though generally related/interdependent. So both when
    outputting info to a user and for internal operations at different times we
    need refer to just the repo name (e.g., for state directory location), just
    the template name (e.g., for state file location, context variables), and
    both (e.g., to uniquely identify the template in some user messaging).

    This class papers over those differences.
    """

    SEPARATOR: ClassVar[str] = ":"

    repo_name: str
    template_name: str

    @classmethod
    def parse(cls, s: Self | TemplateId | str) -> Self:
        if isinstance(s, cls):
            return s

        return cls.from_str(cast(str, s))

    @classmethod
    def from_str(cls, s: TemplateId | str) -> Self:
        parts = s.split(cls.SEPARATOR)

        if len(parts) == 1:
            return cls(repo_name=parts[0], template_name=parts[0])
        else:
            return cls(repo_name=parts[0], template_name=cls.SEPARATOR.join(parts[1:]))

    @property
    def id(self) -> TemplateId:
        if self.repo_name == self.template_name:
            return TemplateId(self.repo_name)

        return TemplateId(self.SEPARATOR.join([self.repo_name, self.template_name]))

    @property
    def answers_file_prefix(self) -> str:
        if self.repo_name == self.template_name:
            return ""

        return self.template_name + "-"

    def is_singular_instance(self, app_name: str) -> bool:
        """Check if this app_name implies the template only exists once for project.

        Effectively, when the app name is the same name as the template itself
        (barring some special cases), assume the template is something which
        only has one instance in a given project.
        """
        # special case templates with the name "app", which by convention
        # shouldn't be unique and if someone wants to install an instance of the
        # template as "app" instead of "example-app"/a name that corresponds to
        # its purpose, well...let them
        if self.template_name == "app":
            return False

        return app_name == self.template_name
