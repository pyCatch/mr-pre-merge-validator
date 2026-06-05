from mr_validator.domain.models import Commit, MergeRequest
from mr_validator.services.ticket_extractor import TicketExtractor


def test_extracts_ticket_from_title() -> None:
    """Ensure a Jira ticket is extracted from the merge request title."""
    merge_request = MergeRequest(
        iid=1,
        title="WMS-1234: Add validation",
        description="",
        source_branch="feature/no-ticket",
        is_draft=False,
        commits=(),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ("WMS-1234",)


def test_extracts_ticket_from_source_branch() -> None:
    """Ensure a Jira ticket is extracted from the merge request source branch."""
    merge_request = MergeRequest(
        iid=1,
        title="Add validation",
        description="",
        source_branch="feature/WMS-1234-add-validation",
        is_draft=False,
        commits=(),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ("WMS-1234",)


def test_extracts_ticket_from_description() -> None:
    """Ensure a Jira ticket is extracted from the merge request description."""
    merge_request = MergeRequest(
        iid=1,
        title="Add validation",
        description="Related Jira ticket: WMS-1234",
        source_branch="feature/add-validation",
        is_draft=False,
        commits=(),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ("WMS-1234",)


def test_extracts_ticket_from_commit_message() -> None:
    """Ensure a Jira ticket is extracted from commit messages."""
    merge_request = MergeRequest(
        iid=1,
        title="Add validation",
        description="",
        source_branch="feature/add-validation",
        is_draft=False,
        commits=(
            Commit(
                title="Update validation tests",
                message="WMS-1234: cover ticket extraction",
            ),
        ),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ("WMS-1234",)


def test_extracts_unique_tickets_when_same_ticket_appears_multiple_times() -> None:
    """Ensure duplicate Jira tickets are returned only once."""
    merge_request = MergeRequest(
        iid=1,
        title="WMS-1234: Add validation",
        description="Related to WMS-1234",
        source_branch="feature/WMS-1234-add-validation",
        is_draft=False,
        commits=(
            Commit(
                title="WMS-1234: update tests",
                message="WMS-1234 appears again",
            ),
        ),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ("WMS-1234",)


def test_extracts_tickets_from_all_sources_without_duplicates() -> None:
    """Ensure Jira tickets are collected from all MR sources without duplicates."""
    merge_request = MergeRequest(
        iid=1,
        title="WMS-1234: Add validation",
        description="Related to WMS-5678",
        source_branch="feature/WMS-1234-add-validation",
        is_draft=False,
        commits=(
            Commit(
                title="WMS-9012: update tests",
                message="Also mentions WMS-5678",
            ),
        ),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ("WMS-1234", "WMS-5678", "WMS-9012")


def test_returns_empty_tuple_when_no_tickets_found() -> None:
    """Ensure an empty tuple is returned when no Jira tickets are found."""
    merge_request = MergeRequest(
        iid=1,
        title="Add validation",
        description="No Jira ticket here",
        source_branch="feature/add-validation",
        is_draft=False,
        commits=(
            Commit(
                title="Update tests",
                message="No ticket here either",
            ),
        ),
    )

    tickets = TicketExtractor().extract_from_merge_request(merge_request)

    assert tickets == ()