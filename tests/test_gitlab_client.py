import pytest
from pytest_httpx import HTTPXMock

from mr_validator.clients.gitlab_client import GITLAB_API_PREFIX, GitLabClient
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
    assert mr.description == "Description"
    assert mr.source_branch == "feature/WMS-1234-add-foo"
    assert mr.is_draft is False
    assert len(mr.commits) == 1
    assert mr.commits[0].title == "commit 1"
    assert mr.commits[0].message == "message 1"


@pytest.mark.asyncio
async def test_get_merge_request_converts_missing_description_to_empty_string(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure GitLab client converts missing MR description to an empty string."""
    httpx_mock.add_response(
        json={
            "iid": 1,
            "title": "WMS-1234: Add foo",
            "description": None,
            "source_branch": "feature/WMS-1234-add-foo",
            "draft": False,
        }
    )
    httpx_mock.add_response(json=[])

    client = GitLabClient(Settings())

    mr = await client.get_merge_request(
        project="test/project",
        mr_iid=1,
    )

    assert mr.description == ""


@pytest.mark.asyncio
async def test_get_merge_request_maps_draft_to_is_draft(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure GitLab draft field is mapped to domain is_draft flag."""
    httpx_mock.add_response(
        json={
            "iid": 1,
            "title": "WMS-1234: Add foo",
            "description": "Description",
            "source_branch": "feature/WMS-1234-add-foo",
            "draft": True,
        }
    )
    httpx_mock.add_response(json=[])

    client = GitLabClient(Settings())

    mr = await client.get_merge_request(
        project="test/project",
        mr_iid=1,
    )

    assert mr.is_draft is True


@pytest.mark.asyncio
async def test_get_merge_request_url_encodes_project_path(
    httpx_mock: HTTPXMock,
) -> None:
    """Ensure GitLab project path is URL-encoded in API requests."""
    httpx_mock.add_response(
        url=f"https://gitlab.com{GITLAB_API_PREFIX}/projects/group%2Fproject/merge_requests/1",
        json={
            "iid": 1,
            "title": "WMS-1234: Add foo",
            "description": "Description",
            "source_branch": "feature/WMS-1234-add-foo",
            "draft": False,
        },
    )
    httpx_mock.add_response(
        url=f"https://gitlab.com{GITLAB_API_PREFIX}/projects/group%2Fproject/merge_requests/1/commits",
        json=[],
    )

    client = GitLabClient(Settings())

    mr = await client.get_merge_request(
        project="group/project",
        mr_iid=1,
    )

    assert mr.iid == 1