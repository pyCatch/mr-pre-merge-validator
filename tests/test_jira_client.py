import pytest
from pytest_httpx import HTTPXMock

from mr_validator.clients.jira_client import JiraClient
from mr_validator.config import Settings


@pytest.mark.asyncio
async def test_get_issue_returns_jira_issue(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure Jira client returns a parsed Jira issue."""
    httpx_mock.add_response(
        json={
            "key": "WMS-1234",
            "fields": {
                "status": {
                    "name": "In Progress",
                },
                "issuetype": {
                    "name": "Task",
                },
            },
        }
    )

    client = JiraClient(Settings())

    issue = await client.get_issue("WMS-1234")

    assert issue.key == "WMS-1234"
    assert issue.status == "In Progress"
    assert issue.issue_type == "Task"