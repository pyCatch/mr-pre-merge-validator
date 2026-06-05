from unittest.mock import AsyncMock, Mock, call

import httpx
import pytest

from mr_validator.application.validate_merge_request import ValidateMergeRequestUseCase
from mr_validator.domain.models import JiraIssue, MergeRequest
from mr_validator.domain.validation import CheckStatus

TEST_PROJECT = "example/project"
TEST_MR_IID = 1


def make_merge_request(
    *,
    is_draft: bool = False,
    title: str = "WMS-1001: Add bearer-token auth",
    description: str = "",
    source_branch: str = "feature/WMS-1001-bearer-auth",
) -> MergeRequest:
    return MergeRequest(
        iid=1,
        title=title,
        description=description,
        source_branch=source_branch,
        is_draft=is_draft,
        commits=(),
    )


def make_jira_issue(
    *,
    key: str = "WMS-1001",
    status: str = "In Review",
    issue_type: str = "Story",
) -> JiraIssue:
    return JiraIssue(
        key=key,
        status=status,
        issue_type=issue_type,
    )


def make_not_found_error(ticket_key: str = "WMS-404") -> httpx.HTTPStatusError:
    request = httpx.Request("GET", f"http://localhost:8080/rest/api/3/issue/{ticket_key}")
    response = httpx.Response(status_code=404, request=request)
    return httpx.HTTPStatusError("Issue not found", request=request, response=response)


def make_use_case(
    *,
    merge_request: MergeRequest | None = None,
    ticket_keys: tuple[str, ...] = ("WMS-1001",),
    jira_issue: JiraIssue | Exception | None = None,
) -> tuple[ValidateMergeRequestUseCase, AsyncMock, AsyncMock, Mock]:
    gitlab_client = AsyncMock()
    jira_client = AsyncMock()
    ticket_extractor = Mock()

    gitlab_client.get_merge_request.return_value = merge_request or make_merge_request()
    ticket_extractor.extract_from_merge_request.return_value = ticket_keys

    if isinstance(jira_issue, Exception):
        jira_client.get_issue.side_effect = jira_issue
    else:
        jira_client.get_issue.return_value = jira_issue or make_jira_issue()

    use_case = ValidateMergeRequestUseCase(
        gitlab_client=gitlab_client,
        jira_client=jira_client,
        ticket_extractor=ticket_extractor,
    )

    return use_case, gitlab_client, jira_client, ticket_extractor


@pytest.mark.asyncio
async def test_execute_passes_when_merge_request_is_valid() -> None:
    """Ensure validation succeeds for a non-draft MR with a valid Jira ticket."""
    use_case, gitlab_client, jira_client, ticket_extractor = make_use_case()

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is True
    assert result.exit_code == 0
    assert all(check.status == CheckStatus.PASS for check in result.checks)

    gitlab_client.get_merge_request.assert_awaited_once_with(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )
    ticket_extractor.extract_from_merge_request.assert_called_once()
    jira_client.get_issue.assert_awaited_once_with("WMS-1001")


@pytest.mark.asyncio
async def test_execute_fails_when_merge_request_is_draft() -> None:
    """Ensure validation fails when the merge request is marked as draft."""
    use_case, _, _, _ = make_use_case(
        merge_request=make_merge_request(is_draft=True),
    )

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is False
    assert result.exit_code == 1
    assert result.checks[0].status == CheckStatus.FAIL
    assert result.checks[0].name == "MR is not Draft"


@pytest.mark.asyncio
async def test_execute_fails_when_no_jira_tickets_are_referenced() -> None:
    """Ensure validation fails when no Jira tickets are found in the MR."""
    use_case, _, jira_client, _ = make_use_case(ticket_keys=())

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is False
    assert result.exit_code == 1
    assert result.checks[-1].status == CheckStatus.FAIL
    assert result.checks[-1].name == "Jira tickets referenced"
    jira_client.get_issue.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_fails_when_jira_ticket_does_not_exist() -> None:
    """Ensure validation fails when the referenced Jira ticket does not exist."""
    use_case, _, _, _ = make_use_case(
        ticket_keys=("WMS-404",),
        jira_issue=make_not_found_error("WMS-404"),
    )

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is False
    assert result.exit_code == 1
    assert any(
        check.status == CheckStatus.FAIL and check.name == "WMS-404 exists in Jira"
        for check in result.checks
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["Open", "In Progress", "Won't Do"])
async def test_execute_fails_when_jira_ticket_status_is_not_mergeable(status: str) -> None:
    """Ensure validation fails for Jira tickets in non-mergeable statuses."""
    use_case, _, _, _ = make_use_case(
        jira_issue=make_jira_issue(status=status),
    )

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is False
    assert result.exit_code == 1
    assert any(
        check.status == CheckStatus.FAIL and check.name == "WMS-1001 has mergeable status"
        for check in result.checks
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["In Review", "Done"])
async def test_execute_passes_when_jira_ticket_status_is_mergeable(status: str) -> None:
    """Ensure validation succeeds for Jira tickets in mergeable statuses."""
    use_case, _, _, _ = make_use_case(
        jira_issue=make_jira_issue(status=status),
    )

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is True
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_execute_passes_when_all_referenced_tickets_are_mergeable() -> None:
    """Ensure validation succeeds when all referenced Jira tickets are mergeable."""
    jira_client = AsyncMock()
    jira_client.get_issue.side_effect = [
        make_jira_issue(key="WMS-1001", status="In Review"),
        make_jira_issue(key="WMS-1002", status="Done"),
    ]

    gitlab_client = AsyncMock()
    gitlab_client.get_merge_request.return_value = make_merge_request()

    ticket_extractor = Mock()
    ticket_extractor.extract_from_merge_request.return_value = ("WMS-1001", "WMS-1002")

    use_case = ValidateMergeRequestUseCase(
        gitlab_client=gitlab_client,
        jira_client=jira_client,
        ticket_extractor=ticket_extractor,
    )

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is True
    assert result.exit_code == 0
    assert all(check.status == CheckStatus.PASS for check in result.checks)
    assert jira_client.get_issue.await_count == 2
    jira_client.get_issue.assert_has_awaits(
        [
            call("WMS-1001"),
            call("WMS-1002"),
        ]
    )


@pytest.mark.asyncio
async def test_execute_fails_when_one_of_multiple_tickets_is_not_mergeable() -> None:
    """Ensure validation fails when at least one Jira ticket is not mergeable."""
    jira_client = AsyncMock()
    jira_client.get_issue.side_effect = [
        make_jira_issue(key="WMS-1001", status="In Review"),
        make_jira_issue(key="WMS-1002", status="Open"),
    ]

    gitlab_client = AsyncMock()
    gitlab_client.get_merge_request.return_value = make_merge_request()

    ticket_extractor = Mock()
    ticket_extractor.extract_from_merge_request.return_value = ("WMS-1001", "WMS-1002")

    use_case = ValidateMergeRequestUseCase(
        gitlab_client=gitlab_client,
        jira_client=jira_client,
        ticket_extractor=ticket_extractor,
    )

    result = await use_case.execute(
        project=TEST_PROJECT,
        mr_iid=TEST_MR_IID,
    )

    assert result.passed is False
    assert result.exit_code == 1
    assert any(
        check.status == CheckStatus.FAIL and check.name == "WMS-1002 has mergeable status"
        for check in result.checks
    )
    assert jira_client.get_issue.await_count == 2
    jira_client.get_issue.assert_has_awaits(
        [
            call("WMS-1001"),
            call("WMS-1002"),
        ]
    )