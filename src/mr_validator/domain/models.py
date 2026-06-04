from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Commit:
    title: str
    message: str


@dataclass(frozen=True, slots=True)
class MergeRequest:
    iid: int
    title: str
    description: str
    source_branch: str
    is_draft: bool
    commits: tuple[Commit, ...]


@dataclass(frozen=True, slots=True)
class JiraIssue:
    key: str
    status: str
    issue_type: str