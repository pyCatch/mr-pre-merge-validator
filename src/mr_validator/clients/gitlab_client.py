from urllib.parse import quote_plus

import httpx

from mr_validator.config import Settings
from mr_validator.domain.models import Commit, MergeRequest


class GitLabClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_merge_request(
        self,
        project: str,
        mr_iid: int,
    ) -> MergeRequest:
        encoded_project = quote_plus(project)

        async with httpx.AsyncClient(
            base_url=self._settings.gitlab_base_url,
            timeout=self._settings.request_timeout_seconds,
        ) as client:
            mr_response = await client.get(
                f"/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}"
            )
            mr_response.raise_for_status()

            commits_response = await client.get(
                f"/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}/commits"
            )
            commits_response.raise_for_status()

        mr_data = mr_response.json()
        commits_data = commits_response.json()

        commits = tuple(
            Commit(
                title=commit["title"],
                message=commit["message"],
            )
            for commit in commits_data
        )

        return MergeRequest(
            iid=mr_data["iid"],
            title=mr_data["title"],
            description=mr_data.get("description") or "",
            source_branch=mr_data["source_branch"],
            is_draft=mr_data["draft"],
            commits=commits,
        )