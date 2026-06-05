import pytest
from pytest_httpx import HTTPXMock

from mr_validator.clients.gitlab_client import GitLabClient
from mr_validator.config import Settings


@pytest.mark.asyncio
async def test_get_merge_request_returns_merge_request(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure GitLab client returns a parsed merge request with commits."""
    httpx_mock.add_response(
        json={
            "iid": 1,
            "title": "WMS-1234: Add foo",
            "description": "Description",
            "source_branch": "feature/WMS-1234-add-foo",
            "draft": False,
        }
    )

    httpx_mock.add_response(
        json=[
            {
                "title": "commit 1",
                "message": "message 1",
            }
        ]
    )

    client = GitLabClient(Settings())

    mr = await client.get_merge_request(
        project="test/project",
        mr_iid=1,
    )

    assert mr.iid == 1
    assert mr.title == "WMS-1234: Add foo"
    assert len(mr.commits) == 1