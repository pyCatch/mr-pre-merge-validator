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