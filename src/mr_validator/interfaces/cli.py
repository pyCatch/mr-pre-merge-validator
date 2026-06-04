import argparse
import asyncio

import httpx

from mr_validator.application.validate_merge_request import ValidateMergeRequestUseCase
from mr_validator.clients.gitlab_client import GitLabClient
from mr_validator.clients.jira_client import JiraClient
from mr_validator.config import Settings
from mr_validator.services.ticket_extractor import TicketExtractor


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
) -> int:
    settings = Settings()

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

    for check in result.checks:
        print(f"[{check.status.value}] {check.name}: {check.message}")

    print("Result: PASSED" if result.passed else "Result: FAILED")

    return result.exit_code


async def async_main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "validate":
            return await run_validate(
                project=args.project,
                mr_iid=args.mr_iid,
            )

        return 2
    except httpx.ConnectError:
        settings = Settings()
        print("[ERROR] Cannot connect to Jira server.")
        print(f"URL: {settings.jira_base_url}")
        print()
        print("Please start mock Jira:")
        print("python mock_jira.py")
        return 2

    except httpx.HTTPStatusError as error:
        print("[ERROR] HTTP request failed.")
        print(
            f"Status code: "
            f"{error.response.status_code}"

        )
        return 2

    except Exception as error:
        print("[ERROR] Unexpected runtime error.")
        print(str(error))
        return 2



def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()