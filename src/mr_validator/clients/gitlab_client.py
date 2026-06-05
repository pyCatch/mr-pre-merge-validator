import logging
from urllib.parse import quote_plus

import httpx

from mr_validator.config import Settings
from mr_validator.domain.models import Commit, MergeRequest
from mr_validator.services.retry import retryable_request

logger = logging.getLogger(__name__)

GITLAB_API_PREFIX = "/api/v4"

class GitLabClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_merge_request(
        self,
        project: str,
        mr_iid: int,
    ) -> MergeRequest:
        encoded_project = quote_plus(project)

        logger.info(
            "Fetching GitLab merge request: project=%s mr_iid=%s",
            project,
            mr_iid,
        )

        logger.debug(
            "Encoded GitLab project path: %s",
            encoded_project,
        )

        async with httpx.AsyncClient(
            base_url=self._settings.gitlab_base_url,
            timeout=self._settings.request_timeout_seconds,
        ) as client:
            mr_response = await self._fetch_merge_request_response(
                client=client,
                encoded_project=encoded_project,
                mr_iid=mr_iid,
            )
            commits_response = await self._fetch_commits_response(
                client=client,
                encoded_project=encoded_project,
                mr_iid=mr_iid,
            )

        mr_data = mr_response.json()
        commits_data = commits_response.json()

        logger.debug(
            "GitLab merge request response loaded: iid=%s",
            mr_data.get("iid"),
        )

        logger.debug(
            "GitLab merge request commits loaded: count=%s",
            len(commits_data),
        )

        commits = tuple(
            Commit(
                title=commit["title"],
                message=commit["message"],
            )
            for commit in commits_data
        )

        logger.info(
            "GitLab merge request loaded: iid=%s commits=%s",
            mr_data["iid"],
            len(commits),
        )

        return MergeRequest(
            iid=mr_data["iid"],
            title=mr_data["title"],
            description=mr_data.get("description") or "",
            source_branch=mr_data["source_branch"],
            is_draft=mr_data["draft"],
            commits=commits,
        )

    @retryable_request()
    async def _fetch_merge_request_response(
        self,
        client: httpx.AsyncClient,
        encoded_project: str,
        mr_iid: int,
    ) -> httpx.Response:
        response = await client.get(
            f"{GITLAB_API_PREFIX}/projects/{encoded_project}/merge_requests/{mr_iid}"
        )
        response.raise_for_status()
        return response

    @retryable_request()
    async def _fetch_commits_response(
        self,
        client: httpx.AsyncClient,
        encoded_project: str,
        mr_iid: int,
    ) -> httpx.Response:
        response = await client.get(
            f"{GITLAB_API_PREFIX}/projects/{encoded_project}/merge_requests/{mr_iid}/commits"
        )
        response.raise_for_status()
        return response