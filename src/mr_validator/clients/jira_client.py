import httpx

from mr_validator.config import Settings
from mr_validator.domain.models import JiraIssue


class JiraClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_issue(
        self,
        ticket_key: str,
    ) -> JiraIssue:
        async with httpx.AsyncClient(
            base_url=self._settings.jira_base_url,
            timeout=self._settings.request_timeout_seconds,
        ) as client:
            response = await client.get(
                f"/rest/api/2/issue/{ticket_key}",
                headers={
                    "Authorization": f"Bearer {self._settings.jira_token}",
                },
            )

            response.raise_for_status()

        data = response.json()

        fields = data["fields"]

        return JiraIssue(
            key=data["key"],
            status=fields["status"]["name"],
            issue_type=fields["issuetype"]["name"],
        )