DEFAULT_MERGE_CONFLICT_MSG = "Merge conflicts detected, they will need to be resolved manually."


class MergeConflictsDuringUpdateError(Exception):
    message: str | None
    commit_msg: str | None

    def __init__(
        self,
        message: str | None = DEFAULT_MERGE_CONFLICT_MSG,
        commit_msg: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.commit_msg = commit_msg
