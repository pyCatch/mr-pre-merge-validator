import re

from mr_validator.domain.models import Commit, MergeRequest

JIRA_TICKET_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")


class TicketExtractor:
    def extract_from_merge_request(self, merge_request: MergeRequest) -> tuple[str, ...]:
        sources = [
            merge_request.title,
            merge_request.source_branch,
            merge_request.description,
            *self._commit_texts(merge_request.commits),
        ]

        tickets: list[str] = []

        for source in sources:
            for ticket in JIRA_TICKET_PATTERN.findall(source):
                if ticket not in tickets:
                    tickets.append(ticket)

        return tuple(tickets)

    def _commit_texts(self, commits: tuple[Commit, ...]) -> tuple[str, ...]:
        return tuple(
            text
            for commit in commits
            for text in (commit.title, commit.message)
        )