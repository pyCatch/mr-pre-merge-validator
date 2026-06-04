import asyncio
import logging

import httpx

from mr_validator.clients.gitlab_client import GitLabClient
from mr_validator.clients.jira_client import JiraClient
from mr_validator.domain.models import JiraIssue
from mr_validator.domain.validation import CheckStatus, ValidationCheck, ValidationResult
from mr_validator.services.ticket_extractor import TicketExtractor

logger = logging.getLogger(__name__)

ALLOWED_JIRA_STATUSES = {"In Review", "Done"}


class ValidateMergeRequestUseCase:
    def __init__(
        self,
        gitlab_client: GitLabClient,
        jira_client: JiraClient,
        ticket_extractor: TicketExtractor,
    ) -> None:
        self._gitlab_client = gitlab_client
        self._jira_client = jira_client
        self._ticket_extractor = ticket_extractor

    async def execute(self, project: str, mr_iid: int) -> ValidationResult:
        checks: list[ValidationCheck] = []
        logger.info("Fetching merge request from GitLab: project=%s mr_iid=%s", project, mr_iid)

        merge_request = await self._gitlab_client.get_merge_request(
            project=project,
            mr_iid=mr_iid,
        )
        logger.debug(
            "Merge request loaded: iid=%s title=%s source_branch=%s is_draft=%s commits=%s",
            merge_request.iid,
            merge_request.title,
            merge_request.source_branch,
            merge_request.is_draft,
            len(merge_request.commits),
        )

        logger.info("Checking draft status")
        checks.append(
            self._build_check(
                name="MR is not Draft",
                passed=not merge_request.is_draft,
                success_message="Merge request is ready for review.",
                failure_message="Merge request is Draft. Mark it as ready before merging.",
            )
        )

        logger.info("Extracting referenced Jira tickets")
        ticket_keys = self._ticket_extractor.extract_from_merge_request(merge_request)
        logger.debug("Extracted Jira tickets: %s", ticket_keys)

        checks.append(
            self._build_check(
                name="Jira tickets referenced",
                passed=bool(ticket_keys),
                success_message=f"Found Jira ticket(s): {', '.join(ticket_keys)}",
                failure_message="No Jira tickets found in title, branch, description, or commits.",
            )
        )

        if not ticket_keys:
            logger.info("Validation stopped: no Jira tickets found")
            return ValidationResult(checks=tuple(checks))

        logger.info("Fetching referenced Jira issues: count=%s", len(ticket_keys))
        issue_results = await asyncio.gather(
            *(self._get_issue_or_none(ticket_key) for ticket_key in ticket_keys)
        )

        for ticket_key, issue in zip(ticket_keys, issue_results, strict=True):
            logger.debug(
                "Validating Jira issue result: key=%s found=%s",
                ticket_key,
                issue is not None
            )
            checks.append(
                self._build_check(
                    name=f"{ticket_key} exists in Jira",
                    passed=issue is not None,
                    success_message=f"{ticket_key} exists.",
                    failure_message=f"{ticket_key} does not exist in Jira.",
                )
            )

            if issue is None:
                continue

            checks.append(
                self._build_check(
                    name=f"{ticket_key} has mergeable status",
                    passed=issue.status in ALLOWED_JIRA_STATUSES,
                    success_message=f"{ticket_key} status is {issue.status}.",
                    failure_message=(
                        f"{ticket_key} status is {issue.status}. "
                        "Expected In Review or Done."
                    ),
                )
            )

        logger.info("Validation checks completed: total=%s", len(checks))
        return ValidationResult(checks=tuple(checks))

    async def _get_issue_or_none(self, ticket_key: str) -> JiraIssue | None:
        try:
            return await self._jira_client.get_issue(ticket_key)
        except httpx.HTTPStatusError as error:
            logger.debug(
                "Jira issue request failed: key=%s status_code=%s",
                ticket_key,
                error.response.status_code,
            )
            if error.response.status_code == 404:
                return None
            raise

    @staticmethod
    def _build_check(
        name: str,
        passed: bool,
        success_message: str,
        failure_message: str,
    ) -> ValidationCheck:
        return ValidationCheck(
            name=name,
            status=CheckStatus.PASS if passed else CheckStatus.FAIL,
            message=success_message if passed else failure_message,
        )