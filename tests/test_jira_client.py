import httpx
import pytest
from pytest_httpx import HTTPXMock

from mr_validator.clients.jira_client import JIRA_API_PREFIX, JiraClient
from mr_validator.config import Settings


@pytest.mark.asyncio
async def test_get_issue_returns_jira_issue(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure Jira client returns a parsed Jira issue."""
    httpx_mock.add_response(
        url=f"http://localhost:8080{JIRA_API_PREFIX}/issue/WMS-1234",
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
        },
    )

    client = JiraClient(Settings())

    issue = await client.get_issue("WMS-1234")

    assert issue.key == "WMS-1234"
    assert issue.status == "In Progress"
    assert issue.issue_type == "Task"


@pytest.mark.asyncio
async def test_get_issue_sends_bearer_token_authorization_header(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure Jira client sends bearer token authorization header."""
    httpx_mock.add_response(
        match_headers={"Authorization": "Bearer dummy-token"},
        json={
            "key": "WMS-1234",
            "fields": {
                "status": {"name": "In Review"},
                "issuetype": {"name": "Story"},
            },
        },
    )

    client = JiraClient(Settings())

    issue = await client.get_issue("WMS-1234")

    assert issue.key == "WMS-1234"


@pytest.mark.asyncio
async def test_get_issue_uses_jira_api_v3_endpoint(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure Jira client uses Jira REST API v3 issue endpoint."""
    httpx_mock.add_response(
        url=f"http://localhost:8080{JIRA_API_PREFIX}/issue/WMS-1234",
        json={
            "key": "WMS-1234",
            "fields": {
                "status": {"name": "Done"},
                "issuetype": {"name": "Bug"},
            },
        },
    )

    client = JiraClient(Settings())

    issue = await client.get_issue("WMS-1234")

    assert issue.status == "Done"
    assert issue.issue_type == "Bug"


@pytest.mark.asyncio
async def test_get_issue_raises_http_status_error_when_issue_not_found(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure Jira client propagates 404 errors for missing Jira issues."""
    httpx_mock.add_response(
        url=f"http://localhost:8080{JIRA_API_PREFIX}/issue/WMS-404",
        status_code=404,
        json={"errorMessages": ["Issue does not exist"]},
    )

    client = JiraClient(Settings())

    with pytest.raises(httpx.HTTPStatusError):
        await client.get_issue("WMS-404")