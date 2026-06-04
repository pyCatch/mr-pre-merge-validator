import argparse
import asyncio
import logging

import httpx

from mr_validator.application.validate_merge_request import ValidateMergeRequestUseCase
from mr_validator.clients.gitlab_client import GitLabClient
from mr_validator.clients.jira_client import JiraClient
from mr_validator.config import Settings
from mr_validator.logging import configure_logging
from mr_validator.services.report_builder import CliReportRenderer
from mr_validator.services.ticket_extractor import TicketExtractor

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mr-validator",
        description="Validate GitLab merge requests before merge.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a GitLab merge request against Jira workflow rules.",
    )
    validate_parser.add_argument(
        "--project",
        required=True,
        help="GitLab project path, for example: sztomi/mr-validator-homework.",
    )
    validate_parser.add_argument(
        "--mr-iid",
        required=True,
        type=int,
        help="GitLab merge request IID.",
    )

    return parser


async def run_validate(
    project: str,
    mr_iid: int,
    settings: Settings,
) -> int:
    logger.info("Starting MR validation: project=%s mr_iid=%s", project, mr_iid)
    gitlab_client = GitLabClient(settings)
    jira_client = JiraClient(settings)
    ticket_extractor = TicketExtractor()

    use_case = ValidateMergeRequestUseCase(
        gitlab_client=gitlab_client,
        jira_client=jira_client,
        ticket_extractor=ticket_extractor,
    )

    result = await use_case.execute(
        project=project,
        mr_iid=mr_iid,
    )

    logger.info(
        "MR validation completed: project=%s mr_iid=%s passed=%s exit_code=%s",
        project,
        mr_iid,
        result.passed,
        result.exit_code,
    )
    CliReportRenderer().render(result)

    return result.exit_code


async def async_main() -> int:
    settings = Settings()
    configure_logging(settings.log_level)
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "validate":
            return await run_validate(
                project=args.project,
                mr_iid=args.mr_iid,
                settings=settings,
            )

        return 2
    except httpx.ConnectError:
        logger.error("Cannot connect to Jira server: url=%s", settings.jira_base_url)
        print("[ERROR] Cannot connect to Jira server.")
        print(f"URL: {settings.jira_base_url}")
        print()
        print("Please start mock Jira:")
        print("python mock_jira.py")
        return 2

    except httpx.HTTPStatusError as error:
        logger.error(
            "HTTP request failed: status_code=%s",
            error.response.status_code,
        )
        print("[ERROR] HTTP request failed.")
        print(f"Status code: {error.response.status_code}")
        return 2

    except Exception as error:
        logger.exception("Unexpected runtime error")
        print("[ERROR] Unexpected runtime error.")
        print(str(error))
        return 2


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()